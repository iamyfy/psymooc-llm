from typing import Dict
from .schemas import SessionState, PatientProfile, PatientPersona
from .record_generator import generate_profile_and_persona

_sessions: Dict[str, SessionState] = {}

DEFAULT_PROFILE = PatientProfile(
    demographics={
        "name": "张某",
        "gender": "男",
        "age": "17",                
        "occupation": "学生",
        "marriage": "未婚",
        "education": "重点高中",
    },
    chief_complaint="情绪异常波动，讲话滔滔不绝，常语无伦次",
    history={
        "onset": "数周前",
        "course": "情绪高涨与愤怒交替，症状逐渐加重",
        "triggers": "学习压力, 家庭矛盾, 父母高期待",
        "past_psych": "无",
        "past_medical": "无重大躯体病史或手术史",
        "substance": "否认",
        "family_history": "无精神疾病或重大躯体疾病史",
        "personal_history": "自幼在城市成长，童年内敛，高中后性格稍显外向，升学压力显著"
    },
    mental_status_exam={
        "consciousness": "清醒",
        "orientation": "完整",
        "attention": "涣散，难以集中",
        "mood": "欣快与愤怒交替",
        "thought": "思维奔逸，联想松散，夸大妄想",
        "perception": "听觉幻觉，被害妄想",
        "cognition": "欠佳",
        "insight": "缺失",
        "speech": "多语，语速快，语无伦次"
    },
    diagnosis="躁狂发作",
    severity="重度",
    risk={"suicide": "无", "self_harm": "否认"},
)


DEFAULT_PERSONA = PatientPersona(
    traits= ["激动", "多语", "自信过度", "容易分心"],
    style= "语速快、语无伦次",
    insight_level= 0.1,
    trust_toward_clinician= 0.4,
    cooperativeness= 0.5,
    emotional_reactivity= 0.9,
    verbosity= 0.9,
    disclosure_threshold= 0.7,
    lie_propensity= 0.3,
    omission_strategy= "deny"
)

def get_session_state(session_id: str) -> SessionState:
    if session_id not in _sessions:
        try:
            # 从默认 profile 中取年龄、性别、诊断和严重程度作为输入
            age = DEFAULT_PROFILE.demographics.get("age", "")
            gender = DEFAULT_PROFILE.demographics.get("gender", "")
            diagnosis = DEFAULT_PROFILE.diagnosis
            severity = DEFAULT_PROFILE.severity
            profile, persona = generate_profile_and_persona(age, gender, diagnosis, severity)
            # 如果生成出的对象包含部分有效信息，则使用它，否则回退到默认值
            if profile and profile.demographics:
                patient_profile = profile
            else:
                patient_profile = DEFAULT_PROFILE
            if persona and getattr(persona, "traits", []):
                patient_persona = persona
            else:
                patient_persona = DEFAULT_PERSONA
        except Exception:
            # 出现异常时使用默认
            patient_profile = DEFAULT_PROFILE
            patient_persona = DEFAULT_PERSONA
        _sessions[session_id] = SessionState(
            patient_profile=patient_profile,
            patient_persona=patient_persona,
            stage="opening",
            dialog_history=[],
            beliefs={}
        )
    return _sessions[session_id]

def set_session_state(session_id: str, state: SessionState) -> None:
    _sessions[session_id] = state
