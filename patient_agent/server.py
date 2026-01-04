import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from .schemas import WSInPayload
from .state import get_session_state, set_session_state
from .policy import patient_chain

app = FastAPI(title="Patient Agent v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

active_tasks: Dict[str, asyncio.Task] = {}

@app.websocket("/ws/{session_id}")
async def ws_chat(ws: WebSocket, session_id: str):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_json()
            try:
                payload = WSInPayload(**data)
            except Exception as e:
                await ws.send_json({"type":"error","data": f"Invalid payload: {e}"})
                continue

            state = get_session_state(session_id)
            if payload.profile: state.patient_profile = payload.profile
            if payload.persona: state.patient_persona = payload.persona
            if payload.stage: state.stage = payload.stage

            if payload.text:
                state.dialog_history.append({"role":"doctor","text":payload.text})
            set_session_state(session_id,state)

            prev=active_tasks.get(session_id)
            if prev and not prev.done():
                prev.cancel()
                try: await prev
                except: pass

            async def generate_and_stream():
                inputs = {
                    "profile": state.patient_profile.model_dump(),
                    "persona": state.patient_persona.model_dump(),
                    "turn": {"stage": state.stage, "doctor_last_utterance": payload.text},
                    "history": state.dialog_history,
                }
                try:
                    async for ev in patient_chain.astream_events(inputs, version="v1"):
                        evt = ev.get("event")
                        if evt in ("on_chat_model_stream","on_llm_stream"):
                            chunk = ev.get("data",{}).get("chunk",None)
                            token = getattr(chunk,"content",None) if chunk else None
                            if token: await ws.send_json({"type":"token","data":token})
                        elif evt=="on_chain_end":
                            out_text = ev.get("data",{}).get("output","")
                            if out_text:
                                state.dialog_history.append({"role":"patient","text":out_text})
                                set_session_state(session_id,state)
                                await ws.send_json({"type":"final","data":out_text})
                except asyncio.CancelledError:
                    await ws.send_json({"type":"info","data":"generation_cancelled"})
                except Exception as e:
                    await ws.send_json({"type":"error","data":str(e)})
            task=asyncio.create_task(generate_and_stream())
            active_tasks[session_id]=task
    except WebSocketDisconnect:
        prev=active_tasks.get(session_id)
        if prev and not prev.done(): prev.cancel()
