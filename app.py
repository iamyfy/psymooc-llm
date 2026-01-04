#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask API 服务器 - 患者智能体后端
提供REST API接口用于患者模拟和对话
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Api, Resource
import uuid
import logging
from typing import Dict, Any
import traceback

# 导入患者智能体模块
from patient_agent.record_generator import generate_medical_record, parse_patient_profile, parse_patient_persona
from patient_agent.policy import patient_chain
from patient_agent.schemas import PatientProfile, PatientPersona, SessionState
from patient_agent.state import DEFAULT_PROFILE, DEFAULT_PERSONA

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求
api = Api(app)

# 全局会话存储（生产环境建议使用Redis或数据库）
sessions: Dict[str, SessionState] = {}

class PatientCreateResource(Resource):
    """创建新的患者会话"""
    
    def post(self):
        try:
            data = request.get_json()
            
            # 验证必需参数
            required_fields = ['age', 'gender', 'diagnosis', 'severity']
            for field in required_fields:
                if field not in data:
                    return {
                        'success': False,
                        'error': f'缺少必需参数: {field}'
                    }, 400
            
            # 生成会话ID
            session_id = str(uuid.uuid4())
            
            # 调用RAG生成病历
            logger.info(f"为会话 {session_id} 生成病历...")
            record = generate_medical_record(
                age=data['age'],
                gender=data['gender'], 
                diagnosis=data['diagnosis'],
                severity=data['severity']
            )
            
            if not record:
                logger.warning(f"RAG生成失败，使用默认配置")
                profile, persona = DEFAULT_PROFILE, DEFAULT_PERSONA
            else:
                # 解析病历为结构化数据
                profile = parse_patient_profile(record)
                persona = parse_patient_persona(record)
            
            # 创建会话状态
            session_state = SessionState(
                patient_profile=profile,
                patient_persona=persona,
                stage="opening",
                dialog_history=[],
                beliefs={}
            )
            
            # 存储会话
            sessions[session_id] = session_state
            
            logger.info(f"成功创建会话 {session_id}")
            
            return {
                'success': True,
                'session_id': session_id,
                'patient_profile': profile.model_dump(),
                'patient_persona': persona.model_dump(),
                'medical_record': record if record else "使用默认配置"
            }
            
        except Exception as e:
            logger.error(f"创建患者会话失败: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': f'创建会话失败: {str(e)}'
            }, 500

class PatientResource(Resource):
    """获取患者信息"""
    
    def get(self, session_id: str):
        try:
            if session_id not in sessions:
                return {
                    'success': False,
                    'error': '会话不存在'
                }, 404
            
            session = sessions[session_id]
            
            return {
                'success': True,
                'session_id': session_id,
                'patient_profile': session.patient_profile.model_dump(),
                'patient_persona': session.patient_persona.model_dump(),
                'current_stage': session.stage,
                'dialog_count': len(session.dialog_history)
            }
            
        except Exception as e:
            logger.error(f"获取患者信息失败: {str(e)}")
            return {
                'success': False,
                'error': f'获取信息失败: {str(e)}'
            }, 500

class ChatResource(Resource):
    """与患者对话"""
    
    def post(self, session_id: str):
        try:
            if session_id not in sessions:
                return {
                    'success': False,
                    'error': '会话不存在'
                }, 404
            
            data = request.get_json()
            if 'message' not in data:
                return {
                    'success': False,
                    'error': '缺少消息内容'
                }, 400
            
            session = sessions[session_id]
            doctor_message = data['message']
            
            # 构建输入
            inputs = {
                "profile": session.patient_profile.model_dump(),
                "persona": session.patient_persona.model_dump(),
                "turn": {"stage": session.stage, "doctor_last_utterance": doctor_message},
                "history": session.dialog_history,
            }
            
            # 调用患者策略链
            result = patient_chain.invoke(inputs)
            
            # 提取回复
            if isinstance(result, dict):
                patient_reply = str(result.get("reply") or result.get("content") or result)
            else:
                content = getattr(result, "content", None)
                patient_reply = str(content) if content else str(result)
            
            # 更新对话历史
            session.dialog_history.append({"speaker": "doctor", "text": doctor_message})
            session.dialog_history.append({"speaker": "patient", "text": patient_reply})
            
            logger.info(f"会话 {session_id} 对话完成")
            
            return {
                'success': True,
                'session_id': session_id,
                'doctor_message': doctor_message,
                'patient_reply': patient_reply,
                'current_stage': session.stage
            }
            
        except Exception as e:
            logger.error(f"对话失败: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': f'对话失败: {str(e)}'
            }, 500

class HistoryResource(Resource):
    """获取对话历史"""
    
    def get(self, session_id: str):
        try:
            if session_id not in sessions:
                return {
                    'success': False,
                    'error': '会话不存在'
                }, 404
            
            session = sessions[session_id]
            
            return {
                'success': True,
                'session_id': session_id,
                'dialog_history': session.dialog_history,
                'total_turns': len(session.dialog_history)
            }
            
        except Exception as e:
            logger.error(f"获取对话历史失败: {str(e)}")
            return {
                'success': False,
                'error': f'获取历史失败: {str(e)}'
            }, 500

class StageResource(Resource):
    """更新对话阶段"""
    
    def put(self, session_id: str):
        try:
            if session_id not in sessions:
                return {
                    'success': False,
                    'error': '会话不存在'
                }, 404
            
            data = request.get_json()
            if 'stage' not in data:
                return {
                    'success': False,
                    'error': '缺少阶段参数'
                }, 400
            
            new_stage = data['stage']
            valid_stages = ["opening", "information_gathering", "explanation_planning", "closing"]
            
            if new_stage not in valid_stages:
                return {
                    'success': False,
                    'error': f'无效的阶段: {new_stage}，有效值: {valid_stages}'
                }, 400
            
            session = sessions[session_id]
            old_stage = session.stage
            session.stage = new_stage
            
            logger.info(f"会话 {session_id} 阶段从 {old_stage} 更新为 {new_stage}")
            
            return {
                'success': True,
                'session_id': session_id,
                'old_stage': old_stage,
                'new_stage': new_stage
            }
            
        except Exception as e:
            logger.error(f"更新阶段失败: {str(e)}")
            return {
                'success': False,
                'error': f'更新阶段失败: {str(e)}'
            }, 500

class RegenerateResource(Resource):
    """重新生成病历"""
    
    def post(self, session_id: str):
        try:
            if session_id not in sessions:
                return {
                    'success': False,
                    'error': '会话不存在'
                }, 404
            
            session = sessions[session_id]
            profile = session.patient_profile
            
            # 使用当前profile的信息重新生成
            age = profile.demographics.get("age", "16")
            gender = profile.demographics.get("gender", "男")
            diagnosis = profile.diagnosis or "精神分裂症"
            severity = profile.severity or "中度"
            
            logger.info(f"为会话 {session_id} 重新生成病历...")
            
            # 重新生成病历
            record = generate_medical_record(age, gender, diagnosis, severity)
            
            if record:
                # 解析新的病历
                new_profile = parse_patient_profile(record)
                new_persona = parse_patient_persona(record)
                
                # 更新会话
                session.patient_profile = new_profile
                session.patient_persona = new_persona
                
                logger.info(f"会话 {session_id} 病历重新生成成功")
                
                return {
                    'success': True,
                    'session_id': session_id,
                    'new_profile': new_profile.model_dump(),
                    'new_persona': new_persona.model_dump(),
                    'medical_record': record
                }
            else:
                return {
                    'success': False,
                    'error': '病历重新生成失败'
                }, 500
                
        except Exception as e:
            logger.error(f"重新生成病历失败: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': f'重新生成失败: {str(e)}'
            }, 500

class DeleteSessionResource(Resource):
    """删除会话"""
    
    def delete(self, session_id: str):
        try:
            if session_id not in sessions:
                return {
                    'success': False,
                    'error': '会话不存在'
                }, 404
            
            del sessions[session_id]
            logger.info(f"会话 {session_id} 已删除")
            
            return {
                'success': True,
                'message': f'会话 {session_id} 已删除'
            }
            
        except Exception as e:
            logger.error(f"删除会话失败: {str(e)}")
            return {
                'success': False,
                'error': f'删除会话失败: {str(e)}'
            }, 500

# 注册API路由
api.add_resource(PatientCreateResource, '/api/v1/patients/create')
api.add_resource(PatientResource, '/api/v1/patients/<string:session_id>')
api.add_resource(ChatResource, '/api/v1/patients/<string:session_id>/chat')
api.add_resource(HistoryResource, '/api/v1/patients/<string:session_id>/history')
api.add_resource(StageResource, '/api/v1/patients/<string:session_id>/stage')
api.add_resource(RegenerateResource, '/api/v1/patients/<string:session_id>/regenerate')
api.add_resource(DeleteSessionResource, '/api/v1/patients/<string:session_id>')

# 健康检查端点
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'patient-agent-api',
        'active_sessions': len(sessions)
    })

# 根路径
@app.route('/')
def index():
    return jsonify({
        'service': 'Patient Agent API',
        'version': '1.0.0',
        'endpoints': {
            'create_patient': 'POST /api/v1/patients/create',
            'get_patient': 'GET /api/v1/patients/{session_id}',
            'chat': 'POST /api/v1/patients/{session_id}/chat',
            'history': 'GET /api/v1/patients/{session_id}/history',
            'update_stage': 'PUT /api/v1/patients/{session_id}/stage',
            'regenerate': 'POST /api/v1/patients/{session_id}/regenerate',
            'delete_session': 'DELETE /api/v1/patients/{session_id}',
            'health': 'GET /health'
        }
    })

if __name__ == '__main__':
    logger.info("启动Patient Agent API服务器...")
    app.run(host='0.0.0.0', port=5000, debug=True)
