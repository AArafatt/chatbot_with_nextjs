# Chatbot Monorepo (Next.js + FastAPI)

This repo contains a simple chatbot with a Next.js frontend and a FastAPI backend. The backend returns a demo response by default and can call Groq (ChatGroq) if `GROQ_API_KEY` is provided.

## Structure

- `frontend/`: Next.js 14 (App Router, TypeScript). Chat UI at `/chat`.
- `backend/`: FastAPI app with `/chat` and `/health` endpoints.

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+

## Setup

### Backend

1. Create and activate a virtual environment (Windows PowerShell):
   - `cd backend`
   - `py -3 -m venv .venv`
   - `.\\.venv\\Scripts\\Activate.ps1`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Optional: enable real LLM calls by creating `.env` (copy from `.env.example`) and set `GROQ_API_KEY` (and optionally `GROQ_MODEL`, e.g., `llama3-8b-8192`).
4. Run the server:
   - `uvicorn app.main:app --reload --port 8000`

The backend exposes:
- `GET http://localhost:8000/health`
- `POST http://localhost:8000/chat` with body `{ messages: [{ role, content }], temperature? }`

### Frontend

1. In a new terminal:
   - `cd frontend`
   - Copy `.env.local.example` to `.env.local` if needed, adjust `NEXT_PUBLIC_BACKEND_URL`.
   - `npm install` (already run by the scaffold; safe to rerun)
   - `npm run dev`
2. Open `http://localhost:3000/chat` for the chat UI.

## Notes

- CORS is enabled for `http://localhost:3000` by default. If you change ports/origin, set `FRONTEND_ORIGIN` in `backend/.env`.
- Without `GROQ_API_KEY`, the backend replies in demo mode by echoing your last message with a note.
- To change the model, set `GROQ_MODEL` in `backend/.env`.

## Next Steps

- Stream responses (Server-Sent Events or websockets)
- Persist chat history
- Add authentication and rate limiting
