#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
对话评估模块
包含评分 Agent 和反馈 Agent
"""

from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import os

# 初始化 LLM
llm = ChatOpenAI(
    openai_api_key=os.getenv('OPENAI_API_KEY', 'sk-HpDITbMxP8eFnGN3cV5jy3taxkyUnqjtj8ePYxJBZ4MmD8hl'),
    openai_api_base=os.getenv('OPENAI_API_BASE', 'https://api.apicore.ai/v1'),
    model="gpt-4o"
)

# 评分 Agent 的提示词模板
scoring_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一位专业的精神科医学教育评估专家，擅长依据结构化量表对医学生与患者的沟通表现进行客观评分与反馈。

你的任务：阅读“患者信息”和“医学生-患者对话记录”，严格按照以下评分规则评分（总分100），并给出依据。不得编造对话中不存在的内容；如信息缺失，应在说明中标注“对话未体现/证据不足”。

========================
评分规则（总分100）
========================

A. 原则态度（20分）
A1 尊重并理解患者（4分）
- 观察点：称呼得体；避免贬损/标签化；对患者处境表现理解；不否定患者体验。
A2 态度真诚和蔼（4分）
- 观察点：语气温和；表达关怀；非命令式；不冷漠、不敷衍。
A3 以患者为中心的交流方式（4分）
- 观察点：优先关注患者主诉与需求；允许患者决定重点；关照感受、功能与目标；解释围绕患者理解。
A4 知情同意（4分）
- 观察点：说明访谈目的/流程/时长/记录与保密边界；在敏感问题、量表、联系家属、体检/检查等前进行征询；获得同意或给出选择。
A5 没有违背伦理和可能引起纠纷的言语和行为（4分）
- 观察点：不威胁、不诱导、不羞辱；不作无依据承诺；不透露不当隐私；不进行不恰当指责；风险场景下措辞审慎、合规。

B. 基本技巧（50分）
B1 耐心倾听并有恰当反应（10分）
- 观察点：不频繁打断；对关键内容有回应（复述/点头/确认）；跟进线索；体现倾听而非机械问答。
B2 鼓励患者充分表达（5分）
- 观察点：使用鼓励语（“你可以继续说”）；留白；邀请补充；接纳沉默。
B3 提问以开放式为先导，开放和封闭提问妥善结合和转换（10分）
- 观察点：先开放后聚焦；必要时封闭核实；转换自然；避免连珠炮或诱导性提问。
B4 对重要信息和解释有核实（10分）
- 观察点：对时间线、频率、严重度、风险、用药依从性、既往史等进行核对；对患者理解进行“teach-back/确认”；纠正误解时清晰且不冒犯。
B5 提供恰当的具体建议（5分）
- 观察点：建议具体、可执行、与当前阶段匹配（不越界开治疗处方亦可给沟通/就医流程/安全建议）；避免空泛。
B6 清楚表明医生的意见（5分）
- 观察点：明确总结临床判断/下一步方向（如需要进一步了解、评估风险、建议进一步检查/转介等）；表达清晰但不过度下诊断。
B7 有阶段性总结或结束时总结（5分）
- 观察点：阶段性小结或结束总结；包含已获关键信息与下一步；给患者提问机会并确认理解。

C. 效果印象（30分）
C1 达到沟通目的，或未达成但不是医生的问题（10分）
- 观察点：访谈目标清晰；关键问题得到推进；若患者拒答/情绪阻断，医生处理得当并记录限制。
C2 患者感到舒适和被理解（10分）
- 观察点：患者情绪被接住；对抗/防御降低；患者表达更充分；用语让患者更安心。
C3 考官认为考生有较好的沟通能力（10分）
- 观察点：整体结构清晰；节奏良好；专业且有人情味；风险场景处理稳健。

========================
计分要求
========================
- 每个子项按“0~该项满分”给分，允许整数或0.5分。
- 需给出每个子项的简要依据（引用对话中的关键行为/表述特征；不要捏造原句）。
- 计算三大类小计与总分（总分= A小计 + B小计 + C小计）。
- 若对话内容不足以评价某项，不要给高分；应在comment中写明“未体现/证据不足”。

========================
输出格式（严格JSON）
========================
请仅输出一个JSON对象，不要输出任何额外文本。JSON结构如下（字段名必须一致）：
{
  "原则态度": {
    "A1 尊重并理解患者": {"score": 0, "comment": ""},
    "A2 态度真诚和蔼": {"score": 0, "comment": ""},
    "A3 以患者为中心的交流方式": {"score": 0, "comment": ""},
    "A4 知情同意": {"score": 0, "comment": ""},
    "A5 伦理与纠纷风险控制": {"score": 0, "comment": ""},
    "小计": 0
  },
  "基本技巧": {
    "B1 倾听与反应": {"score": 0, "comment": ""},
    "B2 鼓励表达": {"score": 0, "comment": ""},
    "B3 提问结构（开放→封闭）": {"score": 0, "comment": ""},
    "B4 重要信息与解释核实": {"score": 0, "comment": ""},
    "B5 具体建议": {"score": 0, "comment": ""},
    "B6 医生意见表达": {"score": 0, "comment": ""},
    "B7 总结（阶段/结束）": {"score": 0, "comment": ""},
    "小计": 0
  },
  "效果印象": {
    "C1 沟通目的达成度": {"score": 0, "comment": ""},
    "C2 患者舒适与被理解": {"score": 0, "comment": ""},
    "C3 总体沟通能力印象": {"score": 0, "comment": ""},
    "小计": 0
  },
  "总分": 0,
  "主要亮点": ["", ""],
  "主要问题": ["", ""],
  "可操作的改进建议": ["", "", ""]
}

务必保证数值加总一致，且输出为可解析的严格JSON。"""),
    ("human", """请对以下医学生与虚拟患者的对话进行评估：

【患者信息】
{patient_info}

【对话记录】
{dialog_history}

请按照评分规则评分，并仅以严格JSON格式输出。""")
])


# 反馈 Agent 的提示词模板
feedback_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一位经验丰富的精神科临床沟通教学导师，同时熟悉
精神科临床沟通技能评估手册、教学指南与结构化反馈框架。

你的职责是：基于【医学生-患者对话记录】，并结合从专业沟通技能
评估与指导知识库中检索到的相关内容，生成**高度情境化的评价标签
与改进建议**。

在分析过程中，请同时完成以下两层任务：

--------------------------------
一、整体层面（全局评估）
--------------------------------
基于完整的对话历史，对医学生的**整体临床访谈表现**进行综合评价，包括但不限于：
- 访谈结构是否清晰、阶段推进是否合理
- 沟通目标是否明确并逐步推进
- 与患者的互动是否专业、自然、具有治疗联盟潜力
- 是否存在系统性优势或反复出现的沟通短板

该部分应体现你对临床访谈“整体质量”的判断，而非逐句点评。

--------------------------------
二、标签层面（局部技能评估与指导）
--------------------------------
对每一个给定的【沟通技能标签】，请结合其**在具体对话片段中的上下文表现**进行分析：

对每个标签，请完成：
1. **情境解读**  
   - 该标签对应的沟通技能在当前对话语境中本应发挥什么作用
   - 该技能在这一阶段为何重要

2. **表现评估**  
   - 医学生在相关对话中的表现是否体现了该技能
   - 若体现，表现程度如何（充分 / 部分 / 不足 / 未体现）
   - 判断时须紧密结合具体话语方式、节奏、回应策略，而非抽象描述

3. **针对性指导（如表现不足）**  
   - 结合专业沟通技能指南与教学策略，给出**可操作、具体、情境化**的改进建议
   - 建议应指向“下次在类似情境中可以如何说 / 如何做”
   - 避免空泛评价或泛化建议

--------------------------------
分析原则
--------------------------------
- 同时利用你对对话语境的理解能力，以及从外部沟通技能知识库中
检索到的相关评估标准与指导策略
- 避免与对话内容不符的推测；若证据不足，应明确指出
- 语言专业、克制、具有教学针对性，避免情绪化或审判式表述

--------------------------------
输出要求
--------------------------------
- 使用清晰的中文自然段
- 先给出【整体临床访谈表现评估】
- 再按【标签】逐一给出情境化分析与指导
- 重点服务于“教学反馈”和“能力提升”，而非简单评价
"""),
    ("human", """请基于以下信息生成反馈与指导：

【患者信息】
{patient_info}

【医学生-患者对话记录】
{dialog_history}

【沟通技能标签列表】
{tag_list}

请严格按照系统提示完成：
1）整体临床访谈表现评估；
2）围绕每个标签的情境化技能评估与针对性指导。""")
])


# 创建评分链
scoring_chain = scoring_prompt | llm | StrOutputParser()

# 创建反馈链
feedback_chain = feedback_prompt | llm | StrOutputParser()


def format_dialog_history(dialog_history: List[Dict[str, str]]) -> str:
    """格式化对话历史为可读文本"""
    formatted_lines = []
    for i, turn in enumerate(dialog_history, 1):
        speaker = turn.get("speaker") or turn.get("role", "unknown")
        text = turn.get("text", "")
        
        if speaker == "doctor":
            speaker_name = "医生"
        elif speaker == "patient":
            speaker_name = "患者"
        else:
            speaker_name = speaker
        
        formatted_lines.append(f"第{i}轮：")
        formatted_lines.append(f"{speaker_name}：{text}\n")
    
    return "\n".join(formatted_lines)


def format_patient_info(profile: Dict[str, Any], persona: Dict[str, Any]) -> str:
    """格式化患者信息"""
    info_lines = []
    
    # 基本信息
    demographics = profile.get("demographics", {})
    info_lines.append(f"姓名：{demographics.get('name', '未知')}")
    info_lines.append(f"性别：{demographics.get('gender', '未知')}")
    info_lines.append(f"年龄：{demographics.get('age', '未知')}")
    info_lines.append(f"职业：{demographics.get('occupation', '未知')}")
    info_lines.append(f"诊断：{profile.get('diagnosis', '未知')}")
    info_lines.append(f"严重程度：{profile.get('severity', '未知')}")
    info_lines.append(f"主诉：{profile.get('chief_complaint', '无')}")
    
    return "\n".join(info_lines)


def evaluate_dialog(
    dialog_history: List[Dict[str, str]],
    patient_profile: Dict[str, Any],
    patient_persona: Dict[str, Any]
) -> Dict[str, Any]:
    """
    评估对话记录
    
    Args:
        dialog_history: 对话历史记录
        patient_profile: 患者档案
        patient_persona: 患者人格参数
    
    Returns:
        包含评分和反馈的字典
    """
    # 格式化输入
    formatted_history = format_dialog_history(dialog_history)
    patient_info = format_patient_info(patient_profile, patient_persona)
    
    # 调用评分 Agent
    try:
        scoring_input = {
            "patient_info": patient_info,
            "dialog_history": formatted_history
        }
        scoring_result_raw = scoring_chain.invoke(scoring_input)
        
        # 尝试解析 JSON
        try:
            # 提取 JSON 部分（可能包含在 markdown 代码块中）
            if "```json" in scoring_result_raw:
                json_start = scoring_result_raw.find("```json") + 7
                json_end = scoring_result_raw.find("```", json_start)
                scoring_result_raw = scoring_result_raw[json_start:json_end].strip()
            elif "```" in scoring_result_raw:
                json_start = scoring_result_raw.find("```") + 3
                json_end = scoring_result_raw.find("```", json_start)
                scoring_result_raw = scoring_result_raw[json_start:json_end].strip()
            
            scoring_result = json.loads(scoring_result_raw)
        except json.JSONDecodeError:
            # 如果解析失败，使用原始文本
            scoring_result = {"raw_output": scoring_result_raw}
    except Exception as e:
        scoring_result = {"error": f"评分生成失败: {str(e)}"}
    
    # 调用反馈 Agent
    # 从评分结果中提取沟通技能标签列表
    tag_list = []
    if isinstance(scoring_result, dict) and "error" not in scoring_result:
        # 提取所有评分项作为标签
        for category_name, category_data in scoring_result.items():
            if isinstance(category_data, dict) and category_name not in ["总分", "主要亮点", "主要问题", "可操作的改进建议"]:
                for item_name, item_data in category_data.items():
                    if item_name != "小计" and isinstance(item_data, dict):
                        tag_list.append(f"{category_name} - {item_name}")
        
        # 如果没有提取到标签，使用默认标签列表
        if not tag_list:
            tag_list = [
                "原则态度 - A1 尊重并理解患者",
                "原则态度 - A2 态度真诚和蔼",
                "原则态度 - A3 以患者为中心的交流方式",
                "原则态度 - A4 知情同意",
                "原则态度 - A5 伦理与纠纷风险控制",
                "基本技巧 - B1 倾听与反应",
                "基本技巧 - B2 鼓励表达",
                "基本技巧 - B3 提问结构（开放→封闭）",
                "基本技巧 - B4 重要信息与解释核实",
                "基本技巧 - B5 具体建议",
                "基本技巧 - B6 医生意见表达",
                "基本技巧 - B7 总结（阶段/结束）",
                "效果印象 - C1 沟通目的达成度",
                "效果印象 - C2 患者舒适与被理解",
                "效果印象 - C3 总体沟通能力印象"
            ]
    else:
        # 如果评分失败，使用默认标签列表
        tag_list = [
            "原则态度 - A1 尊重并理解患者",
            "原则态度 - A2 态度真诚和蔼",
            "原则态度 - A3 以患者为中心的交流方式",
            "原则态度 - A4 知情同意",
            "原则态度 - A5 伦理与纠纷风险控制",
            "基本技巧 - B1 倾听与反应",
            "基本技巧 - B2 鼓励表达",
            "基本技巧 - B3 提问结构（开放→封闭）",
            "基本技巧 - B4 重要信息与解释核实",
            "基本技巧 - B5 具体建议",
            "基本技巧 - B6 医生意见表达",
            "基本技巧 - B7 总结（阶段/结束）",
            "效果印象 - C1 沟通目的达成度",
            "效果印象 - C2 患者舒适与被理解",
            "效果印象 - C3 总体沟通能力印象"
        ]
    
    try:
        feedback_input = {
            "patient_info": patient_info,
            "dialog_history": formatted_history,
            "tag_list": "\n".join([f"- {tag}" for tag in tag_list])
        }
        feedback_result = feedback_chain.invoke(feedback_input)
    except Exception as e:
        feedback_result = f"反馈生成失败: {str(e)}"
    
    return {
        "scoring": scoring_result,
        "feedback": feedback_result,
        "formatted_dialog": formatted_history,
        "patient_info": patient_info
    }


def generate_dialog_document(
    dialog_history: List[Dict[str, str]],
    patient_profile: Dict[str, Any],
    patient_persona: Dict[str, Any],
    session_id: str,
    evaluation_result: Dict[str, Any] = None
) -> str:
    """
    生成对话记录文档
    
    Args:
        dialog_history: 对话历史
        patient_profile: 患者档案
        patient_persona: 患者人格参数
        session_id: 会话ID
        evaluation_result: 评估结果（可选）
    
    Returns:
        格式化的文档字符串
    """
    from datetime import datetime
    
    doc_lines = []
    doc_lines.append("=" * 80)
    doc_lines.append("精神科问诊对话记录")
    doc_lines.append("=" * 80)
    doc_lines.append(f"\n生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc_lines.append(f"会话ID：{session_id}\n")
    
    # 患者信息
    doc_lines.append("-" * 80)
    doc_lines.append("一、患者基本信息")
    doc_lines.append("-" * 80)
    demographics = patient_profile.get("demographics", {})
    doc_lines.append(f"姓名：{demographics.get('name', '未知')}")
    doc_lines.append(f"性别：{demographics.get('gender', '未知')}")
    doc_lines.append(f"年龄：{demographics.get('age', '未知')}")
    doc_lines.append(f"职业：{demographics.get('occupation', '未知')}")
    doc_lines.append(f"婚姻状况：{demographics.get('marriage', '未知')}")
    doc_lines.append(f"诊断：{patient_profile.get('diagnosis', '未知')}")
    doc_lines.append(f"严重程度：{patient_profile.get('severity', '未知')}")
    doc_lines.append(f"主诉：{patient_profile.get('chief_complaint', '无')}\n")
    
    # 对话记录
    doc_lines.append("-" * 80)
    doc_lines.append("二、对话记录")
    doc_lines.append("-" * 80)
    for i, turn in enumerate(dialog_history, 1):
        speaker = turn.get("speaker") or turn.get("role", "unknown")
        text = turn.get("text", "")
        
        if speaker == "doctor":
            speaker_name = "医生"
        elif speaker == "patient":
            speaker_name = "患者"
        else:
            speaker_name = speaker
        
        doc_lines.append(f"\n【第{i}轮】")
        doc_lines.append(f"{speaker_name}：{text}")
    
    # 评估结果
    if evaluation_result:
        doc_lines.append("\n" + "-" * 80)
        doc_lines.append("三、评估结果")
        doc_lines.append("-" * 80)
        
        # 评分
        scoring = evaluation_result.get("scoring", {})
        if isinstance(scoring, dict) and "error" not in scoring and "raw_output" not in scoring:
            doc_lines.append("\n【评分结果】")
            
            # 显示总分
            if "总分" in scoring:
                doc_lines.append(f"总分：{scoring['总分']}/100分\n")
            
            # 遍历三大类别
            category_names = ["原则态度", "基本技巧", "效果印象"]
            for category_name in category_names:
                if category_name in scoring and isinstance(scoring[category_name], dict):
                    category_data = scoring[category_name]
                    doc_lines.append(f"\n{category_name}：")
                    
                    # 显示小计
                    if "小计" in category_data:
                        doc_lines.append(f"  小计：{category_data['小计']}分")
                    
                    # 显示各项评分
                    for item_name, item_data in category_data.items():
                        if item_name != "小计" and isinstance(item_data, dict):
                            score = item_data.get("score", "N/A")
                            comment = item_data.get("comment", "")
                            max_score = ""
                            # 根据类别和项目确定满分
                            if category_name == "原则态度":
                                max_score = "/4分"
                            elif category_name == "基本技巧":
                                if item_name.startswith("B1"):
                                    max_score = "/10分"
                                elif item_name.startswith("B2") or item_name.startswith("B5") or item_name.startswith("B6") or item_name.startswith("B7"):
                                    max_score = "/5分"
                                else:
                                    max_score = "/10分"
                            elif category_name == "效果印象":
                                max_score = "/10分"
                            
                            doc_lines.append(f"  {item_name}：{score}{max_score}")
                            if comment:
                                doc_lines.append(f"    说明：{comment}")
            
            # 显示主要亮点、问题和改进建议
            if "主要亮点" in scoring and isinstance(scoring["主要亮点"], list):
                doc_lines.append(f"\n主要亮点：")
                for highlight in scoring["主要亮点"]:
                    if highlight:
                        doc_lines.append(f"  - {highlight}")
            
            if "主要问题" in scoring and isinstance(scoring["主要问题"], list):
                doc_lines.append(f"\n主要问题：")
                for issue in scoring["主要问题"]:
                    if issue:
                        doc_lines.append(f"  - {issue}")
            
            if "可操作的改进建议" in scoring and isinstance(scoring["可操作的改进建议"], list):
                doc_lines.append(f"\n可操作的改进建议：")
                for suggestion in scoring["可操作的改进建议"]:
                    if suggestion:
                        doc_lines.append(f"  - {suggestion}")
        elif isinstance(scoring, dict) and "raw_output" in scoring:
            doc_lines.append("\n【评分结果】")
            doc_lines.append("评分结果格式解析失败，原始输出：")
            doc_lines.append(scoring["raw_output"])
        else:
            doc_lines.append("\n评分生成失败或格式错误")
        
        # 反馈
        feedback = evaluation_result.get("feedback", "")
        if feedback:
            doc_lines.append("\n【主观反馈】")
            doc_lines.append(feedback)
    
    doc_lines.append("\n" + "=" * 80)
    
    return "\n".join(doc_lines)