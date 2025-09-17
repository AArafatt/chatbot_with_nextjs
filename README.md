# Chatbot Application (Next.js + FastAPI)

A modern chatbot application with a Next.js frontend and FastAPI backend. The backend can run in demo mode or connect to Groq's LLM API for real AI responses.

## 🚀 Quick Start

### Prerequisites

Before running the application, make sure you have:

- **Node.js 18+** and **npm** (for frontend)
- **Python 3.10+** (for backend)
- **Git** (to clone the repository)

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd chatbot_with_nextjs
   ```

2. **Set up the Backend:**
   
   Navigate to the backend directory and create a virtual environment:
   
   **Windows (PowerShell):**
   ```powershell
   cd backend
   py -3 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   
   **Windows (Command Prompt):**
   ```cmd
   cd backend
   py -3 -m venv .venv
   .venv\Scripts\activate.bat
   ```
   
   **macOS/Linux:**
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   
   Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the Frontend:**
   
   Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

You need to run both the backend and frontend servers simultaneously:

1. **Start the Backend Server:**
   
   In the backend directory (with virtual environment activated):
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   
   The backend will be available at: `http://localhost:8000`

2. **Start the Frontend Server:**
   
   In a new terminal, navigate to the frontend directory:
   ```bash
   cd frontend
   npm run dev
   ```
   
   The frontend will be available at: `http://localhost:3000`

3. **Access the Chat Interface:**
   
   Open your browser and go to: `http://localhost:3000/chat`

## 🔧 Configuration

### Demo Mode (Default)
The application runs in demo mode by default, where the backend echoes your messages with a note. No additional configuration is required.

### Real AI Responses (Optional)
To enable real AI responses using Groq's API:

1. Get a free API key from [Groq Console](https://console.groq.com/)
2. In the `backend` directory, create a `.env` file:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama3-8b-8192
   ```
3. Restart the backend server

## 📁 Project Structure

```
chatbot_with_nextjs/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   └── main.py         # Main FastAPI application
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend
│   ├── src/
│   │   └── app/
│   │       └── chat/       # Chat interface
│   └── package.json        # Node.js dependencies
└── README.md
```

## 🔌 API Endpoints

The backend exposes the following endpoints:

- `GET /health` - Health check endpoint
- `POST /chat` - Chat endpoint
  ```json
  {
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "temperature": 0.7
  }
  ```

## 🛠️ Troubleshooting

### Common Issues

1. **Port already in use:**
   - Backend: Change port with `--port 8001` (or any available port)
   - Frontend: Change port with `npm run dev -- -p 3001`

2. **CORS errors:**
   - Make sure the frontend is running on `http://localhost:3000`
   - Or set `FRONTEND_ORIGIN` in `backend/.env` to match your frontend URL

3. **Python virtual environment issues:**
   - Make sure you're using the correct Python version (3.10+)
   - Try recreating the virtual environment

4. **Node.js/npm issues:**
   - Make sure you have Node.js 18+ installed
   - Try deleting `node_modules` and running `npm install` again

### Getting Help

If you encounter any issues:
1. Check that both servers are running
2. Verify the ports (backend: 8000, frontend: 3000)
3. Check the browser console for any error messages
4. Ensure all dependencies are properly installed
