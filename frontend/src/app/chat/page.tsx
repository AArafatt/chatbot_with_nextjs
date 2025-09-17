"use client";

import { useEffect, useMemo, useRef, useState } from "react";

type Role = "system" | "user" | "assistant";

type Message = {
  role: Role;
  content: string;
};

type Session = {
  session_id: string;
  created_at: string;
  last_active: string;
  message_count: number;
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "system", content: "You are a helpful assistant." },
    { role: "assistant", content: "Hi! Ask me anything." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const backendUrl = useMemo(() => {
    return process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const res = await fetch(`${backendUrl}/sessions`);
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
      }
    } catch (err) {
      console.error("Failed to load sessions:", err);
    }
  };

  const createNewSession = async () => {
    try {
      const res = await fetch(`${backendUrl}/session/create`, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setCurrentSessionId(data.session_id);
        setMessages([
          { role: "system", content: "You are a helpful assistant." },
          { role: "assistant", content: "Hi! Ask me anything." },
        ]);
        loadSessions();
      }
    } catch (err) {
      console.error("Failed to create session:", err);
    }
  };

  const switchToSession = async (sessionId: string) => {
    try {
      const res = await fetch(`${backendUrl}/session/${sessionId}`);
      if (res.ok) {
        const data = await res.json();
        setCurrentSessionId(sessionId);
        const sessionMessages = data.messages.length > 0 
          ? data.messages 
          : [
              { role: "system", content: "You are a helpful assistant." },
              { role: "assistant", content: "Hi! Ask me anything." },
            ];
        setMessages(sessionMessages);
      }
    } catch (err) {
      console.error("Failed to load session:", err);
    }
  };

  const deleteSession = async (sessionId: string) => {
    try {
      const res = await fetch(`${backendUrl}/session/${sessionId}`, { method: "DELETE" });
      if (res.ok) {
        if (currentSessionId === sessionId) {
          setCurrentSessionId(null);
          setMessages([
            { role: "system", content: "You are a helpful assistant." },
            { role: "assistant", content: "Hi! Ask me anything." },
          ]);
        }
        loadSessions();
      }
    } catch (err) {
      console.error("Failed to delete session:", err);
    }
  };

  const sendMessage = async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;
    setLoading(true);
    const userMessage = { role: "user", content: trimmed } as Message;
    setMessages(prev => [...prev, userMessage]);
    setInput("");

    try {
      const res = await fetch(`${backendUrl}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          messages: [userMessage], 
          temperature: 0.2,
          session_id: currentSessionId 
        }),
      });
      if (!res.ok) throw new Error(`Request failed: ${res.status}`);
      const data = await res.json();
      const reply: Message = data.reply;
      setMessages((prev) => [...prev, reply]);
      
      if (!currentSessionId) {
        setCurrentSessionId(data.session_id);
        loadSessions();
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error contacting backend: ${err?.message || err}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen flex">
      <aside className="w-64 border-r bg-black p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="font-semibold text-white">Sessions</h2>
          <button
            onClick={createNewSession}
            className="px-2 py-1 text-sm bg-blue-600 text-white rounded"
          >
            New
          </button>
        </div>
        <div className="space-y-2">
          {sessions.map((session) => (
            <div
              key={session.session_id}
              className={`p-2 rounded cursor-pointer flex justify-between items-center ${
                currentSessionId === session.session_id ? "bg-gray-700" : "bg-gray-800 hover:bg-gray-700"
              }`}
            >
              <div onClick={() => switchToSession(session.session_id)} className="flex-1">
                <div className="text-sm font-medium text-white">
                  Session {session.session_id.slice(0, 8)}
                </div>
                <div className="text-xs text-gray-400">
                  {session.message_count} messages
                </div>
              </div>
              <button
                onClick={() => deleteSession(session.session_id)}
                className="text-red-400 hover:text-red-300 text-sm"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      </aside>
      <div className="flex-1 flex flex-col">
        <header className="border-b p-4">
          <h1 className="text-xl font-semibold">
            Chatbot {currentSessionId && `- ${currentSessionId.slice(0, 8)}`}
          </h1>
        </header>
        <main className="flex-1 max-w-3xl w-full mx-auto p-4 flex flex-col gap-4">
        <div className="flex-1 overflow-y-auto space-y-3 border rounded p-3 bg-white">
          {messages
            .filter((m) => m.role !== "system")
            .map((m, i) => (
              <div
                key={i}
                className={
                  m.role === "user" ? "text-right" : "text-left"
                }
              >
                <div
                  className={
                    "inline-block rounded px-3 py-2 max-w-[80%] " +
                    (m.role === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900")
                  }
                >
                  <span className="whitespace-pre-wrap">{m.content}</span>
                </div>
              </div>
            ))}
          <div ref={bottomRef} />
        </div>
        <div className="flex gap-2">
          <textarea
            className="flex-1 border rounded p-2 h-24 resize-none"
            placeholder="Type a message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            disabled={loading}
          />
          <button
            className="px-4 py-2 rounded bg-black text-white disabled:opacity-50 h-12 self-end"
            onClick={sendMessage}
            disabled={loading}
          >
            {loading ? "Sending..." : "Send"}
          </button>
        </div>
          <p className="text-xs text-gray-500">Backend: {backendUrl}/chat</p>
        </main>
      </div>
    </div>
  );
}

