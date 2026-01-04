from typing import List, Literal, Optional, Dict
from pydantic import BaseModel, Field

Stage = Literal["opening", "information_gathering", "explanation_planning", "closing"]

class PatientProfile(BaseModel):
    demographics: Dict[str, str] = Field(default_factory=dict)   # 基本信息
    chief_complaint: str = ""                                   # 主诉
    history: Dict[str, str] = Field(default_factory=dict)        # 病史
    mental_status_exam: Dict[str, str] = Field(default_factory=dict)  # 精神状态检查
    diagnosis: str = ""                                         # 诊断
    severity: Literal["轻度", "中度", "重度"] = "中度"          # 严重程度
    risk: Dict[str, str] = Field(default_factory=dict)           # 风险评估

class PatientPersona(BaseModel):
    traits: List[str] = Field(default_factory=list)
    style: str = "礼貌、谨慎"
    insight_level: float = 0.6
    trust_toward_clinician: float = 0.5
    cooperativeness: float = 0.5
    emotional_reactivity: float = 0.3
    verbosity: float = 0.5
    disclosure_threshold: float = 0.5
    lie_propensity: float = 0.05
    omission_strategy: str = "vague"

class TurnInput(BaseModel):
    stage: Stage
    doctor_last_utterance: str
    dialog_history: List[Dict[str, str]] = Field(default_factory=list)

class SessionState(BaseModel):
    patient_profile: PatientProfile
    patient_persona: PatientPersona
    stage: Stage = "opening"
    dialog_history: List[Dict[str, str]] = Field(default_factory=list)
    beliefs: Dict[str, str] = Field(default_factory=dict)

class WSInPayload(BaseModel):
    text: str
    stage: Optional[Stage] = None
    profile: Optional[PatientProfile] = None
    persona: Optional[PatientPersona] = None
