#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLI 版患者模拟：
- 不改关键代码（RAG: Part1.py、患者策略链: policy.py 等）
- 直接在 bash 里交互，打印所有 LLM 生成内容
- 流程：输入四个基本参数 -> 调用 RAG 生成并打印完整病历 -> 进入自然语言对话
"""

from __future__ import annotations
import argparse
import os
import sys
from typing import Any, Dict, List
import json

# 保持与现有项目的相对导入一致
from .record_generator import (
    generate_medical_record,
    parse_patient_profile,
    parse_patient_persona,
)
from .policy import patient_chain
from .schemas import PatientProfile, PatientPersona, SessionState
from .state import DEFAULT_PROFILE, DEFAULT_PERSONA

def _print_bar(title: str = "", char: str = "=", width: int = 80):
    line = char * width
    if title:
        print(f"\n{line}\n{title}\n{line}")
    else:
        print(f"\n{line}")

def init_from_rag(age: str, gender: str, diagnosis: str, severity: str) -> tuple[PatientProfile, PatientPersona, str]:
    """
    用 Part1 工作流生成完整病历，并解析出结构化 Profile 与 Persona。
    同时把所有 LLM 生成内容打印出来（Part1 节点里已有 print，会显示 story/symptoms）。
    """
    _print_bar("调用 RAG 生成完整病历")
    record = generate_medical_record(age, gender, diagnosis, severity)
    if not record:
        print("⚠️ 生成失败（record 为空）。请检查 Part1.py、向量库/MD 文档与 API 配置。")
        return PatientProfile(), PatientPersona(), ""

    _print_bar("完整病历（Medical Record）")
    print(record)

    profile = parse_patient_profile(record) if record else PatientProfile()
    persona = parse_patient_persona(record) if record else PatientPersona()

    _print_bar("解析后的 PatientProfile")
    print(json.dumps(profile.model_dump(), indent=2, ensure_ascii=False))

    _print_bar("解析后的 PatientPersona")
    print(json.dumps(persona.model_dump(), indent=2, ensure_ascii=False))

    return profile, persona, record

def extract_reply(result: Any) -> str:
    """兼容不同返回类型，取出患者回复文本。"""
    if isinstance(result, dict):
        # 常见：链返回字典
        return str(result.get("reply") or result.get("content") or result)
    # langchain Message 对象
    content = getattr(result, "content", None)
    if content:
        return str(content)
    return str(result)

def run_cli(age: str, gender: str, diagnosis: str, severity: str, no_rag: bool = False):
    # 1) 先 RAG 生成病历（除非 --no-rag）
    if no_rag:
        _print_bar("跳过 RAG，使用默认 Profile/Persona")
        profile, persona, record = DEFAULT_PROFILE, DEFAULT_PERSONA, ""
    else:
        profile, persona, record = init_from_rag(age, gender, diagnosis, severity)
        if not record:
            _print_bar("回退到默认 Profile/Persona（RAG 失败或未配置）", "-")
            profile, persona = DEFAULT_PROFILE, DEFAULT_PERSONA

    # 2) 初始化会话状态（本地，不经 WebSocket）
    state = SessionState(
        patient_profile=profile,
        patient_persona=persona,
        stage="information_gathering",  # 默认阶段；可用 /stage 命令切换
        dialog_history=[],
        beliefs={}
    )

    _print_bar("进入自然语言对话模式", "=")
    print("小提示：")
    print("  /stage opening|information_gathering|explanation_planning|closing 切换会话阶段")
    print("  /persona 显示当前 persona 参数")
    print("  /profile 显示当前 profile 摘要")
    print("  /regen 重新用当前四参走一遍 RAG（会覆盖当前 profile/persona）")
    print("  /quit 退出\n")

    # 3) 循环对话
    while True:
        try:
            user = input("医生> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not user:
            continue

        # 命令处理
        if user.startswith("/quit"):
            print("Bye.")
            break
        if user.startswith("/stage"):
            parts = user.split()
            if len(parts) == 2:
                state.stage = parts[1].strip()
                print(f"阶段已切换为：{state.stage}")
            else:
                print("用法：/stage opening|information_gathering|explanation_planning|closing")
            continue
        if user.startswith("/persona"):
            _print_bar("当前 PatientPersona")
            print(state.patient_persona.model_dump_json(indent=2, ensure_ascii=False))
            continue
        if user.startswith("/profile"):
            _print_bar("当前 PatientProfile（部分）")
            print(state.patient_profile.model_dump_json(indent=2, ensure_ascii=False))
            continue
        if user.startswith("/regen"):
            _print_bar("重新调用 RAG 生成病历")
            profile, persona, record = init_from_rag(
                age=state.patient_profile.demographics.get("age", age) or age,
                gender=state.patient_profile.demographics.get("gender", gender) or gender,
                diagnosis=state.patient_profile.diagnosis or diagnosis,
                severity=state.patient_profile.severity or severity,
            )
            if profile and persona:
                state.patient_profile = profile
                state.patient_persona = persona
                print("✅ 已用 RAG 结果覆盖当前 Profile/Persona。")
            else:
                print("⚠️ RAG 失败，保留原有 Profile/Persona。")
            continue

        # 4) 发送给策略链，并打印 LLM 回复
        #    为了最大限度“打印所有 LLM 内容”，我们把回复完整输出
        inputs = {
            "profile": state.patient_profile.model_dump(),
            "persona": state.patient_persona.model_dump(),
            "turn": {"stage": state.stage, "doctor_last_utterance": user},
            "history": state.dialog_history,
        }
        result = patient_chain.invoke(inputs)
        reply = extract_reply(result)

        # 打印与维护对话历史
        print(f"患者> {reply}")
        state.dialog_history.append({"speaker": "doctor", "text": user})
        state.dialog_history.append({"speaker": "patient", "text": reply})


def main():
    parser = argparse.ArgumentParser(description="CLI 版患者模拟：RAG 生成病历 + 自然语言对话")
    parser.add_argument("--age", default="16", help="年龄（字符串）")
    parser.add_argument("--gender", default="男", help="性别")
    parser.add_argument("--diagnosis", default="躁狂症", help="诊断")
    parser.add_argument("--severity", default="重度", help="严重程度")
    parser.add_argument("--no-rag", action="store_true", help="跳过 RAG，仅用默认 Profile/Persona")
    args = parser.parse_args()
    run_cli(args.age, args.gender, args.diagnosis, args.severity, no_rag=args.no_rag)

if __name__ == "__main__":
    main()