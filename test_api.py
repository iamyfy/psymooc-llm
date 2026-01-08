#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Patient Agent API 测试脚本
用于测试API端点的功能
"""

import requests
import json
import time
import sys

# 配置
BASE_URL = "http://localhost:5000"
TEST_SESSION_ID = None

def test_health_check():
    """测试健康检查端点"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过: {data}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_create_patient():
    """测试创建患者会话"""
    print("\n🔍 测试创建患者会话...")
    try:
        data = {
            "age": "25",
            "gender": "女",
            "diagnosis": "精神分裂症",
            "severity": "中度"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/patients/create", json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                global TEST_SESSION_ID
                TEST_SESSION_ID = result['session_id']
                print(f"✅ 创建会话成功: {TEST_SESSION_ID}")
                print(f"   患者姓名: {result['patient_profile']['demographics'].get('name', 'N/A')}")
                print(f"   诊断: {result['patient_profile']['diagnosis']}")
                return True
            else:
                print(f"❌ 创建会话失败: {result.get('error')}")
                return False
        else:
            print(f"❌ 创建会话失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 创建会话异常: {e}")
        return False

def test_get_patient():
    """测试获取患者信息"""
    if not TEST_SESSION_ID:
        print("❌ 跳过获取患者信息测试 - 没有有效会话ID")
        return False
        
    print(f"\n🔍 测试获取患者信息 (会话: {TEST_SESSION_ID})...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/patients/{TEST_SESSION_ID}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 获取患者信息成功")
                print(f"   当前阶段: {result['current_stage']}")
                print(f"   对话轮数: {result['dialog_count']}")
                return True
            else:
                print(f"❌ 获取患者信息失败: {result.get('error')}")
                return False
        else:
            print(f"❌ 获取患者信息失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取患者信息异常: {e}")
        return False

def test_chat():
    """测试对话功能"""
    if not TEST_SESSION_ID:
        print("❌ 跳过对话测试 - 没有有效会话ID")
        return False
        
    print(f"\n🔍 测试对话功能 (会话: {TEST_SESSION_ID})...")
    try:
        # 第一轮对话
        data = {"message": "你好，请介绍一下你的情况"}
        response = requests.post(f"{BASE_URL}/api/v1/patients/{TEST_SESSION_ID}/chat", json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 第一轮对话成功")
                print(f"   医生: {result['doctor_message']}")
                print(f"   患者: {result['patient_reply'][:100]}...")
                
                # 第二轮对话
                time.sleep(1)  # 避免请求过快
                data2 = {"message": "你最近有什么困扰吗？"}
                response2 = requests.post(f"{BASE_URL}/api/v1/patients/{TEST_SESSION_ID}/chat", json=data2)
                
                if response2.status_code == 200:
                    result2 = response2.json()
                    if result2.get('success'):
                        print(f"✅ 第二轮对话成功")
                        print(f"   医生: {result2['doctor_message']}")
                        print(f"   患者: {result2['patient_reply'][:100]}...")
                        return True
                    else:
                        print(f"❌ 第二轮对话失败: {result2.get('error')}")
                        return False
                else:
                    print(f"❌ 第二轮对话失败: {response2.status_code}")
                    return False
            else:
                print(f"❌ 第一轮对话失败: {result.get('error')}")
                return False
        else:
            print(f"❌ 第一轮对话失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 对话测试异常: {e}")
        return False

def test_get_history():
    """测试获取对话历史"""
    if not TEST_SESSION_ID:
        print("❌ 跳过对话历史测试 - 没有有效会话ID")
        return False
        
    print(f"\n🔍 测试获取对话历史 (会话: {TEST_SESSION_ID})...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/patients/{TEST_SESSION_ID}/history")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 获取对话历史成功")
                print(f"   总对话轮数: {result['total_turns']}")
                for i, turn in enumerate(result['dialog_history'][-4:], 1):  # 显示最后4轮
                    speaker = "医生" if turn['speaker'] == 'doctor' else "患者"
                    text = turn['text'][:50] + "..." if len(turn['text']) > 50 else turn['text']
                    print(f"   {i}. {speaker}: {text}")
                return True
            else:
                print(f"❌ 获取对话历史失败: {result.get('error')}")
                return False
        else:
            print(f"❌ 获取对话历史失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取对话历史异常: {e}")
        return False

def test_update_stage():
    """测试更新对话阶段"""
    if not TEST_SESSION_ID:
        print("❌ 跳过更新阶段测试 - 没有有效会话ID")
        return False
        
    print(f"\n🔍 测试更新对话阶段 (会话: {TEST_SESSION_ID})...")
    try:
        data = {"stage": "information_gathering"}
        response = requests.put(f"{BASE_URL}/api/v1/patients/{TEST_SESSION_ID}/stage", json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 更新对话阶段成功")
                print(f"   从 {result['old_stage']} 更新为 {result['new_stage']}")
                return True
            else:
                print(f"❌ 更新对话阶段失败: {result.get('error')}")
                return False
        else:
            print(f"❌ 更新对话阶段失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 更新对话阶段异常: {e}")
        return False

def test_regenerate():
    """测试重新生成病历"""
    if not TEST_SESSION_ID:
        print("❌ 跳过重新生成测试 - 没有有效会话ID")
        return False
        
    print(f"\n🔍 测试重新生成病历 (会话: {TEST_SESSION_ID})...")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/patients/{TEST_SESSION_ID}/regenerate")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 重新生成病历成功")
                print(f"   新患者姓名: {result['new_profile']['demographics'].get('name', 'N/A')}")
                return True
            else:
                print(f"❌ 重新生成病历失败: {result.get('error')}")
                return False
        else:
            print(f"❌ 重新生成病历失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 重新生成病历异常: {e}")
        return False

def test_evaluate_dialog():
    """测试评估对话并生成文档"""
    if not TEST_SESSION_ID:
        print("❌ 跳过评估对话测试 - 没有有效会话ID")
        return False
    
    # 确保有对话记录
    try:
        history_response = requests.get(f"{BASE_URL}/api/v1/patients/{TEST_SESSION_ID}/history")
        if history_response.status_code == 200:
            history_data = history_response.json()
            dialog_count = len(history_data.get('dialog_history', []))
        else:
            dialog_count = 0
    except:
        dialog_count = 0
    
    if dialog_count == 0:
        print("⚠️  会话中没有对话记录，先进行几轮对话...")
        # 进行几轮测试对话
        test_chat_messages = [
            "你好，请介绍一下你的情况",
            "你什么时候开始出现这些症状的？",
            "能详细描述一下你的感受吗？"
        ]
        for msg in test_chat_messages:
            requests.post(f"{BASE_URL}/api/v1/patients/{TEST_SESSION_ID}/chat", 
                        json={"message": msg})
            time.sleep(1)  # 等待一下
    
    print(f"\n🔍 测试评估对话 (会话: {TEST_SESSION_ID})...")
    print("   注意：此测试可能需要较长时间（10-30秒）...")
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/v1/patients/{TEST_SESSION_ID}/evaluate", timeout=60)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 评估对话成功 (耗时: {elapsed_time:.1f}秒)")
                
                # 显示评分结果
                scoring = result.get('evaluation', {}).get('scoring', {})
                if isinstance(scoring, dict) and '总分' in scoring:
                    print(f"   总分: {scoring['总分']}/100分")
                    # 显示各类别小计
                    for category in ['原则态度', '基本技巧', '效果印象']:
                        if category in scoring and isinstance(scoring[category], dict):
                            subtotal = scoring[category].get('小计', 'N/A')
                            print(f"   {category}小计: {subtotal}分")
                    # 显示主要亮点和问题
                    if '主要亮点' in scoring and isinstance(scoring['主要亮点'], list):
                        highlights = [h for h in scoring['主要亮点'] if h]
                        if highlights:
                            print(f"   主要亮点: {highlights[0]}")
                    if '主要问题' in scoring and isinstance(scoring['主要问题'], list):
                        issues = [i for i in scoring['主要问题'] if i]
                        if issues:
                            print(f"   主要问题: {issues[0]}")
                elif isinstance(scoring, dict) and 'raw_output' in scoring:
                    print(f"   ⚠️  评分结果解析失败，返回原始输出")
                
                # 显示反馈摘要
                feedback = result.get('evaluation', {}).get('feedback', '')
                if feedback:
                    feedback_preview = feedback[:150] + "..." if len(feedback) > 150 else feedback
                    print(f"   反馈预览: {feedback_preview}")
                
                # 检查文档
                document = result.get('document', '')
                if document:
                    print(f"   文档长度: {len(document)} 字符")
                    # 可选：保存文档到文件
                    try:
                        filename = f"dialog_report_{TEST_SESSION_ID}.txt"
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(document)
                        print(f"   ✅ 文档已保存到: {filename}")
                    except Exception as e:
                        print(f"   ⚠️  保存文档失败: {e}")
                
                return True
            else:
                print(f"❌ 评估对话失败: {result.get('error')}")
                return False
        else:
            print(f"❌ 评估对话失败: {response.status_code}")
            if response.status_code == 400:
                print(f"   可能原因: 会话中没有对话记录")
            return False
    except requests.exceptions.Timeout:
        print(f"❌ 评估对话超时（超过60秒）")
        return False
    except Exception as e:
        print(f"❌ 评估对话异常: {e}")
        return False

def test_delete_session():
    """测试删除会话"""
    if not TEST_SESSION_ID:
        print("❌ 跳过删除会话测试 - 没有有效会话ID")
        return False
        
    print(f"\n🔍 测试删除会话 (会话: {TEST_SESSION_ID})...")
    try:
        response = requests.delete(f"{BASE_URL}/api/v1/patients/{TEST_SESSION_ID}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 删除会话成功: {result['message']}")
                return True
            else:
                print(f"❌ 删除会话失败: {result.get('error')}")
                return False
        else:
            print(f"❌ 删除会话失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 删除会话异常: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("Patient Agent API 测试套件")
    print("=" * 60)
    print(f"测试目标: {BASE_URL}")
    print("=" * 60)
    
    # 测试列表
    tests = [
        ("健康检查", test_health_check),
        ("创建患者会话", test_create_patient),
        ("获取患者信息", test_get_patient),
        ("对话功能", test_chat),
        ("获取对话历史", test_get_history),
        ("更新对话阶段", test_update_stage),
        ("重新生成病历", test_regenerate),
        ("评估对话并生成文档", test_evaluate_dialog),
        ("删除会话", test_delete_session),
    ]
    
    # 执行测试
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    # 输出结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"总测试数: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("⚠️  部分测试失败，请检查服务器状态")
        sys.exit(1)

if __name__ == '__main__':
    main()









