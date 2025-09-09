from __future__ import annotations

import os
from typing import List, Literal, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None
    temperature: Optional[float] = 0.2


class ChatResponse(BaseModel):
    reply: Message


app = FastAPI(title="Chatbot Backend", version="0.1.0")

load_dotenv()

# CORS for local Next.js dev
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


def call_groq(messages: List[Message], model: Optional[str] = None, temperature: float = 0.2) -> Optional[str]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    try:
        from groq import Groq

        client = Groq(api_key=api_key)

        # Ensure messages are plain dicts for the API
        payload_messages = [
            m.model_dump() if isinstance(m, BaseModel) else m  # type: ignore[arg-type]
            for m in messages
        ]

        response = client.chat.completions.create(
            model=model or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            messages=payload_messages,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        print(f"Groq call failed: {e}")
        return None


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Try Groq (ChatGroq) if configured
    completion = call_groq(req.messages, req.model, req.temperature or 0.2)
    if completion is None:
        # Fallback response (simple echo/heuristic)
        user_last = next((m.content for m in reversed(req.messages) if m.role == "user"), "")
        completion = (
            "(Demo mode) You said: "
            + user_last
            + "\nSet GROQ_API_KEY to enable real model responses."
        )

    return ChatResponse(reply=Message(role="assistant", content=completion))


# To run: uvicorn app.main:app --reload --port 8000
