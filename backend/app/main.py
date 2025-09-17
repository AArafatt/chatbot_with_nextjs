from __future__ import annotations

import os
from typing import List, Literal, Optional, Dict
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uuid

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str
    timestamp: Optional[datetime] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None
    temperature: Optional[float] = 0.2
    session_id: Optional[str] = None  # Add session ID to request


class ChatResponse(BaseModel):
    reply: Message
    session_id: str  # Return session ID in response


class SessionInfo(BaseModel):
    session_id: str
    created_at: datetime
    last_active: datetime
    messages: List[Message]


# In-memory storage for chat sessions
# In production, you'd use a database like MongoDB, PostgreSQL, or Redis
chat_sessions: Dict[str, SessionInfo] = {}


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


# Session management endpoints
@app.post("/session/create")
def create_session() -> dict:
    """Create a new chat session"""
    session_id = str(uuid.uuid4())
    now = datetime.now()
    chat_sessions[session_id] = SessionInfo(
        session_id=session_id,
        created_at=now,
        last_active=now,
        messages=[]
    )
    return {"session_id": session_id, "created_at": now}


@app.get("/session/{session_id}")
def get_session(session_id: str) -> SessionInfo:
    """Get session information and message history"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return chat_sessions[session_id]


@app.delete("/session/{session_id}")
def delete_session(session_id: str) -> dict:
    """Delete a chat session"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        return {"message": "Session deleted successfully"}
    raise HTTPException(status_code=404, detail="Session not found")


@app.get("/sessions")
def list_sessions() -> List[dict]:
    """List all active sessions (for debugging/admin purposes)"""
    return [
        {
            "session_id": session.session_id,
            "created_at": session.created_at,
            "last_active": session.last_active,
            "message_count": len(session.messages)
        }
        for session in chat_sessions.values()
    ]


# -------------------------------
# LangChain-based Groq Integration
# -------------------------------

def call_groq_with_langchain(messages: List[Message], model: Optional[str] = None, temperature: float = 0.2) -> Optional[str]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

        # Map Pydantic messages to LangChain message types
        lc_messages = []
        for msg in messages:
            if msg.role == "system":
                lc_messages.append(SystemMessage(content=msg.content))
            elif msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))

        # Initialize LangChain ChatGroq model
        chat_model = ChatGroq(
            model=model or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            temperature=temperature,
            groq_api_key=api_key
        )

        # Get response
        response = chat_model.invoke(lc_messages)
        return response.content

    except Exception as e:
        print(f"LangChain Groq call failed: {e}")
        return None


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Handle session management
    if req.session_id:
        # Use existing session
        if req.session_id not in chat_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        session = chat_sessions[req.session_id]
        # Add new messages to session history
        session.messages.extend(req.messages)
    else:
        # Create new session
        session_id = str(uuid.uuid4())
        now = datetime.now()
        chat_sessions[session_id] = SessionInfo(
            session_id=session_id,
            created_at=now,
            last_active=now,
            messages=req.messages.copy()
        )
        session = chat_sessions[session_id]
    
    # Update last active time
    session.last_active = datetime.now()
    
    # Try LangChain Groq if configured
    completion = call_groq_with_langchain(session.messages, req.model, req.temperature or 0.2)
    if completion is None:
        # Fallback response (simple echo/heuristic)
        user_last = next((m.content for m in reversed(session.messages) if m.role == "user"), "")
        completion = (
            "(Demo mode) You said: "
            + user_last
            + "\nSet GROQ_API_KEY to enable real model responses."
        )

    # Create assistant message and add to session
    assistant_message = Message(role="assistant", content=completion)
    session.messages.append(assistant_message)
    
    return ChatResponse(reply=assistant_message, session_id=session.session_id)


# Optional: Cleanup endpoint for inactive sessions (in production, use a background task)
@app.post("/cleanup")
def cleanup_sessions(max_age_hours: int = 24) -> dict:
    """Remove sessions older than max_age_hours"""
    from datetime import timedelta
    now = datetime.now()
    expired_sessions = [
        session_id for session_id, session in chat_sessions.items()
        if (now - session.last_active) > timedelta(hours=max_age_hours)
    ]
    
    for session_id in expired_sessions:
        del chat_sessions[session_id]
    
    return {
        "message": f"Cleaned up {len(expired_sessions)} expired sessions",
        "expired_sessions": expired_sessions
    }
