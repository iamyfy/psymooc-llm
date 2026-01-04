from __future__ import annotations
import os
import sys
import re
from typing import Tuple
import traceback
from .schemas import PatientProfile, PatientPersona


from pathlib import Path

# 使用 pathlib 来处理路径可以避免字符串没有 `.parent` 属性的问题。
_CUR_DIR: Path = Path(__file__).resolve().parent
PROJECT_ROOT: Path = _CUR_DIR.parent

# 将项目根目录添加到 sys.path 中，确保在不同工作目录下也能正确导入 Part1
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# 尝试导入 Part1.py，其中包含 RAG 工作流程；导入失败时缓存错误信息
try:
    import Part1  # 引入 Part1.py，其中定义了 workflow
    _part1_import_error: str | None = None
except Exception as e:
    Part1 = None  # 如果失败，则留空，后面调用会返回默认值
    import traceback as _tb
    _part1_import_error = _tb.format_exc()

def generate_medical_record(age: str, gender: str, diagnosis: str, severity: str) -> str:
    """
    调用 Part1 中的 LangGraph workflow，根据给定的基本信息生成完整病历文本。
    如果 workflow 或依赖不可用，则返回空字符串。
    """
    if Part1 is None:
        print("[RAG ERROR] 无法导入 Part1.py，RAG 工作流不可用。")
        if '_part1_import_error' in globals() and _part1_import_error:
            print(_part1_import_error)
        else:
            print("原因未知（可能是依赖/环境变量/语法错误）。")
        return ""
    if not hasattr(Part1, "workflow"):
        print("[RAG ERROR] Part1 模块缺少 workflow 对象。请检查 Part1.py 的 graph.compile() 与导出。")
        return ""
    workflow = getattr(Part1, "workflow")
    initial_state = {
        "age": str(age),
        "gender": str(gender),
        "diagnosis": str(diagnosis),
        "severity": str(severity),
        "story_retrieved": [],
        "story": "",
        "symptoms_retrieved": [],
        "symptoms": "",
        "medical_record": "",
    }
    try:
        result = workflow.invoke(initial_state)
    except Exception:
        print("[RAG ERROR] 调用 workflow.invoke 失败。初始参数:")
        try:
            # 避免打印敏感信息，这里不打印任何密钥，仅打印业务字段
            safe_state = {k: v for k, v in initial_state.items() if k in ("age","gender","diagnosis","severity")}
            print(safe_state)
        except Exception:
            pass
        traceback.print_exc()
        return ""
    if isinstance(result, dict):
        return result.get("medical_record", "")
    else:
        print(f"[RAG ERROR] workflow 返回非字典类型：{type(result)}，无法提取 medical_record。")
        return ""

def parse_patient_profile(record: str) -> PatientProfile:
    """Parse a RAG‑generated medical record into a ``PatientProfile``.

    The record is expected to follow the eight‑part structure used in
    ``Part1.py``.  This parser extracts information from the labeled
    sections into the appropriate fields of a ``PatientProfile``.  If
    a particular field cannot be found, it will be omitted, causing
    Pydantic to fall back to its default values.

    Note that this parser assumes Chinese punctuation and section
    headings (例如 “一、基本信息”).  If the format deviates, some
    fields may be missing.

    Parameters
    ----------
    record: str
        The full medical record produced by ``generate_medical_record``.

    Returns
    -------
    PatientProfile
        Structured profile populated from the record.
    """
    if not record:
        return PatientProfile()
    # Normalize line endings and remove carriage returns
    txt = record.replace("\r", "")
    # Extract each section using lookahead for the next heading
    def extract_section(start_marker: str, end_marker: str | None) -> str:
        pattern = rf"{re.escape(start_marker)}\s*(.+?)(?={re.escape(end_marker)})" if end_marker else rf"{re.escape(start_marker)}\s*(.+)"
        m = re.search(pattern, txt, re.S)
        return m.group(1).strip() if m else ""
    base = extract_section("一、基本信息", "二、")
    chief = extract_section("二、主诉", "三、")
    present = extract_section("三、现病史", "四、")
    past = extract_section("四、既往史", "五、")
    fam = extract_section("五、家族史", "六、")
    personal = extract_section("六、个人史", "七、")
    exam = extract_section("七、精神状态检查", "八、")
    # Populate demographics and top‑level fields
    demographics: dict[str, str] = {}
    # Name
    m = re.search(r"姓名[:：]\s*([\S]+)", base)
    if m:
        demographics["name"] = m.group(1).strip()
    # Gender
    m = re.search(r"性别[:：]\s*([\S]+)", base)
    if m:
        demographics["gender"] = m.group(1).strip()
    # Age (extract digits)
    m = re.search(r"年龄[:：]\s*(\d+)", base)
    if m:
        demographics["age"] = m.group(1).strip()
    # Occupation
    m = re.search(r"职业[:：]\s*([\S]+)", base)
    if m:
        demographics["occupation"] = m.group(1).strip()
    # Marriage status
    m = re.search(r"婚姻状况[:：]\s*([\S]+)", base)
    if m:
        demographics["marriage"] = m.group(1).strip()
    # Diagnosis
    m = re.search(r"诊断[:：]\s*([\S]+)", base)
    diagnosis = m.group(1).strip() if m else ""
    # Severity
    m = re.search(r"严重程度[:：]\s*([\S]+)", base)
    severity = m.group(1).strip() if m else ""
    # Chief complaint
    chief_complaint = chief.strip().replace("\n", " ") if chief else ""
    # History details
    history: dict[str, str] = {}
    if present:
        # Onset: look for patterns like “数周前”“数月前”“几个月前”
        onset_match = re.search(r"(数\S*前|\d+\s*周前|\d+\s*个月前|\d+\s*年[前]?)", present)
        if onset_match:
            history["onset"] = onset_match.group(1)
        # Course: full present illness description
        history["course"] = present.strip().replace("\n", " ")
        # Triggers: attempt to extract causes after “诱因”
        trig_match = re.search(r"诱因[^，。,]*[，,:：]\s*([^。]+)", present)
        if trig_match:
            # Replace conjunctions with commas
            triggers = trig_match.group(1).replace("和", ",").replace("、", ",")
            history["triggers"] = ", ".join([t.strip() for t in triggers.split(",") if t.strip()])
    # Past history (既往史)
    if past:
        # Past psychiatric history
        if re.search(r"无精神疾病", past):
            history["past_psych"] = "无"
        else:
            history["past_psych"] = past.strip().replace("\n", " ")
        # Past medical history
        if re.search(r"无其他重大躯体疾病", past):
            history["past_medical"] = "无重大躯体病史或手术史"
        # Substance use
        if re.search(r"药物", past) or re.search(r"成瘾", past):
            # Rough classification; mark as present
            history["substance"] = past.strip().replace("\n", " ")
        else:
            history["substance"] = "否认"
    # Family history
    if fam:
        history["family_history"] = fam.strip().replace("\n", " ")
    # Personal history
    if personal:
        history["personal_history"] = personal.strip().replace("\n", " ")
    # Mental status exam
    exam_dict: dict[str, str] = {}
    if exam:
        # Consciousness
        m = re.search(r"意识[:：]\s*([\S]+)", exam)
        if m:
            exam_dict["consciousness"] = m.group(1).strip()
        # Orientation
        m = re.search(r"定向力[:：]\s*([\S]+)", exam)
        if m:
            exam_dict["orientation"] = m.group(1).strip()
        # Attention
        m = re.search(r"注意力[:：]\s*([^\n]+)", exam)
        if m:
            exam_dict["attention"] = m.group(1).strip()
        # Mood/emotion
        m = re.search(r"情绪[:：]\s*([^\n]+)", exam)
        if m:
            exam_dict["mood"] = m.group(1).strip()
        # Thought
        m = re.search(r"思维[:：]\s*([^\n]+)", exam)
        if m:
            exam_dict["thought"] = m.group(1).strip()
        # Perception
        m = re.search(r"知觉[:：]\s*([^\n]+)", exam)
        if m:
            exam_dict["perception"] = m.group(1).strip()
        # Cognition
        m = re.search(r"认知功能[:：]\s*([^\n]+)", exam)
        if m:
            exam_dict["cognition"] = m.group(1).strip()
        # Insight: look for the word “自知力”或“自知力缺失”
        m = re.search(r"自知力[:：]?\s*([^\n]+)", exam)
        if m:
            exam_dict["insight"] = m.group(1).strip()
        else:
            # If cognition contains 自知力缺失，则推断 insight 缺失
            if "自知力" in exam_dict.get("cognition", ""):
                exam_dict["insight"] = "缺失"
        # Speech
        m = re.search(r"语言[:：]\s*([^\n]+)", exam)
        if m:
            exam_dict["speech"] = m.group(1).strip()
    # Build and return PatientProfile
    return PatientProfile(
        demographics=demographics,
        chief_complaint=chief_complaint,
        history=history,
        mental_status_exam=exam_dict,
        diagnosis=diagnosis,
        severity=severity,
        risk={},
    )

def parse_patient_persona(record: str) -> PatientPersona:
    """Parse the persona parameters section of the medical record.

    The eighth section of the record (行为倾向参数) is expected to list
    persona parameters in the following format::

        - traits: ["...", "..."]
        - style: ["...", "..."]
        - insight_level: 0.1
        - trust_toward_clinician: 0.4
        - cooperativeness: 0.5
        - emotional_reactivity: 0.9
        - verbosity: 0.9
        - disclosure_threshold: 0.7
        - lie_propensity: 0.3
        - omission_strategy: deny

    This parser extracts those values using regular expressions.  If a
    parameter is missing or invalid, the default value defined in
    ``PatientPersona`` will be used.

    Parameters
    ----------
    record: str
        The full medical record produced by ``generate_medical_record``.

    Returns
    -------
    PatientPersona
        Populated persona structure.
    """
    if not record:
        return PatientPersona()
    # Locate the eighth section
    m = re.search(r"八、[^\n]*\n(.+)", record, re.S)
    if not m:
        return PatientPersona()
    sec = m.group(1)
    # Traits (list of strings)
    traits: list[str] = []
    m_traits = re.search(r"traits\s*[:：]\s*\[(.*?)\]", sec, re.S)
    if m_traits:
        raw = m_traits.group(1)
        # Split by comma outside quotes
        for part in re.split(r",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", raw):
            item = part.strip().strip("\"' ”“")
            if item:
                traits.append(item)
    # Style (list -> join)
    style = ""
    m_style = re.search(r"style\s*[:：]\s*\[(.*?)\]", sec, re.S)
    if m_style:
        raw = m_style.group(1)
        styles: list[str] = []
        for part in re.split(r",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", raw):
            item = part.strip().strip("\"' ”“")
            if item:
                styles.append(item)
        if styles:
            # Join with Chinese comma for natural phrasing
            style = "、".join(styles)
    # Numeric fields helper
    def extract_float(key: str) -> float | None:
        mm = re.search(rf"{re.escape(key)}\s*[:：]\s*([0-9.]+)", sec)
        if mm:
            try:
                return float(mm.group(1))
            except ValueError:
                return None
        return None
    insight_level = extract_float("insight_level")
    trust = extract_float("trust_toward_clinician")
    cooperativeness = extract_float("cooperativeness")
    emotional_reactivity = extract_float("emotional_reactivity")
    verbosity = extract_float("verbosity")
    disclosure_threshold = extract_float("disclosure_threshold")
    lie_propensity = extract_float("lie_propensity")
    # Omission strategy
    omission_strategy = None
    m_omit = re.search(r"omission_strategy\s*[:：]\s*([\w-]+)", sec)
    if m_omit:
        omission_strategy = m_omit.group(1).strip()
    # Build persona, using defaults where parsing fails
    persona_data = {}
    if traits:
        persona_data["traits"] = traits
    if style:
        persona_data["style"] = style
    if insight_level is not None:
        persona_data["insight_level"] = insight_level
    if trust is not None:
        persona_data["trust_toward_clinician"] = trust
    if cooperativeness is not None:
        persona_data["cooperativeness"] = cooperativeness
    if emotional_reactivity is not None:
        persona_data["emotional_reactivity"] = emotional_reactivity
    if verbosity is not None:
        persona_data["verbosity"] = verbosity
    if disclosure_threshold is not None:
        persona_data["disclosure_threshold"] = disclosure_threshold
    if lie_propensity is not None:
        persona_data["lie_propensity"] = lie_propensity
    if omission_strategy:
        persona_data["omission_strategy"] = omission_strategy
    return PatientPersona(**persona_data)

def generate_profile_and_persona(
    age: str, gender: str, diagnosis: str, severity: str
) -> Tuple[PatientProfile, PatientPersona]:
    """High‑level helper to create a profile and persona for a patient.

    This function invokes the RAG workflow to generate a medical
    record and then parses it into ``PatientProfile`` and
    ``PatientPersona`` objects.  If the workflow or parsing fails,
    default (empty) objects are returned.

    Parameters
    ----------
    age, gender, diagnosis, severity: str
        Basic descriptors to condition the workflow.

    Returns
    -------
    tuple of (PatientProfile, PatientPersona)
        Extracted profile and persona, or defaults on failure.
    """
    record = generate_medical_record(age, gender, diagnosis, severity)
    if not record:
        # Return default objects if generation failed.
        return PatientProfile(), PatientPersona()
    profile = parse_patient_profile(record)
    persona = parse_patient_persona(record)
    return profile, persona