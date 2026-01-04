import json, random
from typing import Any, Dict
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda, RunnableBranch
from langchain_core.output_parsers import StrOutputParser
from .prompts import opening_prompt, info_prompt, plan_prompt, closing_prompt

import os

llm = ChatOpenAI(
    openai_api_key="sk-HpDITbMxP8eFnGN3cV5jy3taxkyUnqjtj8ePYxJBZ4MmD8hl",
    openai_api_base="https://api.apicore.ai/v1",  
    model="gpt-4o"
)
parser = StrOutputParser()

SENSITIVE_HINTS = ["自杀","伤害自己","家暴","性","成瘾","酒精","毒品","药物滥用","犯罪","赌博","怀孕","隐私"]
def is_sensitive_question(text: str) -> bool:
    return any(k in text for k in SENSITIVE_HINTS)

def clamp01(x: float) -> float:
    try: return max(0.0, min(1.0, float(x)))
    except: return 0.5

def _extract_history_context(history: list[Dict[str, Any]], max_rounds: int = 3) -> str:
    # 兼容 {"speaker": ...} 与 {"role": ...}
    def who(item: Dict[str, Any]) -> str:
        v = item.get("speaker") or item.get("role") or ""
        return "医生" if v == "doctor" else ("患者" if v == "patient" else str(v))

    pairs: list[list[Dict[str, Any]]] = []
    buffer: list[Dict[str, Any]] = []
    for item in reversed(history or []):
        buffer.append(item)
        if len(buffer) == 2:
            pairs.append(list(reversed(buffer)))
            buffer = []
        if len(pairs) >= max_rounds:
            break
    pairs.reverse()
    lines: list[str] = []
    for pair in pairs:
        for turn in pair:
            speaker = who(turn)
            text = str(turn.get("text", "")).strip()
            if text:
                lines.append(f"{speaker}: {text}")
    return "\n".join(lines)

def behavior_policy(inputs: Dict[str, Any]) -> Dict[str, Any]:
    profile: Dict[str, Any] = inputs.get("profile", {})
    persona: Dict[str, Any] = inputs.get("persona", {})
    turn: Dict[str, Any] = inputs.get("turn", {})
    history: list[Dict[str, Any]] = inputs.get("history", []) or []
    doctor_q: str = turn.get("doctor_last_utterance", "")

    # 读取并夹取 0-1
    insight = clamp01(persona.get("insight_level", 0.6))
    react  = clamp01(persona.get("emotional_reactivity", 0.4))
    verb   = clamp01(persona.get("verbosity", 0.5))

    trust  = clamp01(persona.get("trust_toward_clinician", 0.5))
    coop   = clamp01(persona.get("cooperativeness", 0.5))
    disc   = clamp01(persona.get("disclosure_threshold", 0.5))

    liep   = clamp01(persona.get("lie_propensity", 0.02))
    omstr  = persona.get("omission_strategy", "vague")
    style  = persona.get("style", "礼貌、谨慎")
    severity = str(profile.get("severity", "中度"))

    # —— Insight 风格
    if insight <= 0.3:
        insight_style = "否认自身问题，倾向将困扰归因于外部环境"
    elif insight <= 0.6:
        insight_style = "意识到可能存在问题，但态度模糊、尚未明确承认"
    else:
        insight_style = "明确承认问题，并希望获得帮助"

    # —— 情绪风格
    if react <= 0.3:
        emotional_style = "情绪抑制明显，表达平淡、内敛"
    elif react <= 0.6:
        emotional_style = "表面情绪稳定，但话语中隐含起伏"
    else:
        emotional_style = "情绪波动明显，可能带有激动、焦虑、愤怒等情绪色彩"

    # —— 回答长度目标
    if verb <= 0.2:
        sentence_target = "回答极简短，极少细节"
    elif verb <= 0.5:
        sentence_target = "表达清晰，偏向简洁，1–2句话带少量细节"
    elif verb <= 0.7:
        sentence_target = "倾向完整表达，会用2–4句话并提供1-2个细节"
    else:
        sentence_target = "表达偏冗长，话多，可能包含4–5句，带有丰富细节甚至会不断重复"

    # —— 敏感判断
    sensitive = is_sensitive_question(doctor_q)
    base_prob = clamp01(0.5 * disc + 0.3 * trust + 0.2 * coop)
    base_prob = clamp01(base_prob - 0.25) if sensitive else clamp01(base_prob + 0.15)

    # —— 披露状态
    if not sensitive:
        disclosure_state = "full_disclose"
    else:
        if base_prob >= 0.75:
            disclosure_state = "full_disclose"
        elif base_prob >= 0.40:
            disclosure_state = "partial_disclose"
        else:
            disclosure_state = "no_disclose"

    # —— 应答语气（真实性维度）
    if disclosure_state == "full_disclose":
        if liep < 0.3: response_tone = "truthful_direct"
        elif liep < 0.6: response_tone = "truth_with_fiction"
        else: response_tone = "fabricated_confident"
    elif disclosure_state == "partial_disclose":
        if liep < 0.3: response_tone = "truthful_evasive"
        elif liep < 0.6: response_tone = "truth_with_omission"
        else: response_tone = "fabricated_partial"
    else:  # no_disclose
        if liep < 0.3: response_tone = "silent_defensive"
        elif liep < 0.6: response_tone = "vague_deflecting"
        else: response_tone = "fabricated_denial"

    # —— 合并映射
    tone_map = {
        "truthful_direct": "真实坦率地作答，给出具体事实",
        "truth_with_fiction": "真实为主，少量润饰/虚构；对非关键细节可能夸大",
        "fabricated_confident": "在非关键细节上编造虚构内容，语气自信连贯",
        "truthful_evasive": "以实话回答，但规避问题核心，更多谈论外围信息",
        "truth_with_omission": "部分真实，对关键细节进行刻意省略与模糊化表达",
        "fabricated_partial": "部分回应问题，对非关键细节作叙事性偏移",
        "silent_defensive": "拒绝回应，态度防御抗拒",
        "vague_deflecting": "模糊措辞与泛化陈述，转移话题",
        "fabricated_denial": "对敏感核心点选择坚决否认或反向叙述，但不得改动诊断/用药/检验等关键事实，保持一致性"
    }

    omission_rule_map = {
        "no": "不回避，直接回应提问要点",
        "vague": "使用模糊措辞，如“可能/大概/不太清楚”等，语义含糊",
        "deny": "直接否认问题前提或事实",
        "omit": "省略关键信息和细节",
        "redirect": "转移话题，引向安全话题或以反问转向",
        "partial": "选择性回应，仅回答非核心问题"
    }

    response_behavior = f"{tone_map.get(response_tone, '未知风格')}；{omission_rule_map.get(omstr, '模糊回避')}"

    # —— 派生布尔量
    will_disclose = disclosure_state in ("full_disclose", "partial_disclose")
    will_lie = response_tone in (
        "truth_with_fiction",
        "fabricated_confident",
        "fabricated_partial",
        "fabricated_denial"
    )

    # traits 字符串化
    traits_val = persona.get("traits", [])
    traits_str = ", ".join(traits_val) if isinstance(traits_val, list) else str(traits_val)

    # —— 历史上下文（最近2-3轮）
    history_context = _extract_history_context(history, max_rounds=3)

    # —— 返回
    return {
        "stage": turn.get("stage", "information_gathering"),
        "doctor_last_utterance": doctor_q,
        "insight_level": insight,
        "trust_toward_clinician": trust,
        "cooperativeness": coop,
        "emotional_reactivity": react,
        "verbosity": verb,
        "disclosure_threshold": disc,
        "lie_propensity": liep,
        "sentence_target": sentence_target,
        "emotional_style": emotional_style,
        "insight_style": insight_style,
        "sensitive": "是" if sensitive else "否",
        "base_disclosure_prob": base_prob,
        "disclosure_state": disclosure_state,
        "response_behavior": response_behavior,   
        "will_disclose": "是" if will_disclose else "否",
        "will_lie": "是" if will_lie else "否",
        "severity": severity,
        "traits": traits_str,
        "style": style,
        "patient_facts": json.dumps(profile, ensure_ascii=False),
        "history_context": history_context,
    }

opening_chain = opening_prompt | llm | parser
info_chain = info_prompt | llm | parser
plan_chain = plan_prompt | llm | parser
closing_chain = closing_prompt | llm | parser

router = RunnableBranch(
    (lambda x: x.get("stage") == "opening", opening_chain),
    (lambda x: x.get("stage") == "information_gathering", info_chain),
    (lambda x: x.get("stage") == "explanation_planning", plan_chain),
    (lambda x: x.get("stage") == "closing", closing_chain),
    info_chain
)

patient_chain = RunnableLambda(behavior_policy) | router