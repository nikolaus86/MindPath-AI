"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import RequireAuth from "@/components/RequireAuth";
import { apiRequest, saveCurrentSession } from "@/lib/api";
import type { ContextFile, Message, Session } from "@/lib/types";

type ChatResponse = {
  user_message: Message;
  assistant_message: Message;
  suggested_app?: string | null;
  suggested_app_title?: string | null;
};

type RouteResponse = {
  recommended_app: string;
  title: string;
  reason: string;
  context: ContextFile;
};

export default function ChatPage() {
  return (
    <RequireAuth>
      <ChatContent />
    </RequireAuth>
  );
}

function ChatContent() {
  const router = useRouter();
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [text, setText] = useState("");
  const [context, setContext] = useState<ContextFile | null>(null);
  const [route, setRoute] = useState<RouteResponse | null>(null);
  const [suggestedApp, setSuggestedApp] = useState<ChatResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function setupSession() {
      const params = new URLSearchParams(window.location.search);
      const querySession = Number(params.get("session"));
      if (Number.isFinite(querySession) && querySession > 0) {
        setSessionId(querySession);
        saveCurrentSession(querySession);
        await loadMessages(querySession);
        return;
      }

      const session = await apiRequest<Session>("/sessions", {
        method: "POST",
        body: JSON.stringify({ title: "New reflection" })
      });
      setSessionId(session.id);
      saveCurrentSession(session.id);
      router.replace(`/chat?session=${session.id}`);
    }

    setupSession().catch((err: Error) => setError(err.message));
  }, [router]);

  async function loadMessages(id: number) {
    const loaded = await apiRequest<Message[]>(`/chat/${id}/messages`);
    setMessages(loaded);
  }

  async function sendMessage(event: FormEvent) {
    event.preventDefault();
    if (!sessionId || !text.trim()) {
      return;
    }

    setError("");
    try {
      const response = await apiRequest<ChatResponse>(`/chat/${sessionId}/messages`, {
        method: "POST",
        body: JSON.stringify({ text })
      });
      setMessages((current) => [...current, response.user_message, response.assistant_message]);
      setText("");
      setContext(null);
      setRoute(null);
      setSuggestedApp(
        response.suggested_app && response.suggested_app_title ? response : null
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not send message");
    }
  }

  async function buildContext() {
    if (!sessionId) {
      return;
    }
    setError("");
    try {
      const savedContext = await apiRequest<ContextFile>(`/context/${sessionId}/build`, {
        method: "POST"
      });
      setContext(savedContext);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not build context");
    }
  }

  async function runRouter() {
    if (!sessionId) {
      return;
    }
    setError("");
    try {
      const response = await apiRequest<RouteResponse>(`/router/${sessionId}/route`, {
        method: "POST"
      });
      setRoute(response);
      setContext(response.context);
      setSuggestedApp(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not route session");
    }
  }

  return (
    <div className="container grid">
      <section className="card">
        <p className="eyebrow">Main chat</p>
        <h1>Describe the situation</h1>
        <p>Write a short message. Then build context and let the router select a mini-app.</p>
      </section>

      <div className="grid grid-2">
        <section className="panel grid">
          <div className="chat-box">
            {messages.map((message) => (
              <div className={`message ${message.role}`} key={message.id}>
                <small>{message.role === "user" ? "You" : "Assistant"}</small>
                {message.text}
              </div>
            ))}
            {messages.length === 0 && <p>No messages yet. Start by describing your problem.</p>}
          </div>

          {suggestedApp?.suggested_app && sessionId && (
            <div className="list-item">
              <strong>AI suggests: {suggestedApp.suggested_app_title}</strong>
              <div className="actions">
                <Link
                  className="button"
                  href={`/apps/${suggestedApp.suggested_app}?session=${sessionId}`}
                >
                  Open mini-app
                </Link>
              </div>
            </div>
          )}

          <form className="form" onSubmit={sendMessage}>
            <label>
              Message
              <textarea
                rows={4}
                value={text}
                onChange={(event) => setText(event.target.value)}
                placeholder="Example: I feel stressed and unsure about choosing my next study plan."
              />
            </label>
            {error && <p className="error">{error}</p>}
            <div className="actions">
              <button className="button" type="submit">Send</button>
              <button className="secondary-button" type="button" onClick={buildContext}>Build context</button>
              <button className="secondary-button" type="button" onClick={runRouter}>Recommend mini-app</button>
            </div>
          </form>
        </section>

        <aside className="grid">
          <section className="panel">
            <h2>Context</h2>
            {context ? (
              <div className="list">
                <div className="list-item"><strong>Problem</strong><p>{context.problem}</p></div>
                <div className="list-item"><strong>Emotion</strong><p>{context.emotion}</p></div>
                <div className="list-item"><strong>Goal</strong><p>{context.goal}</p></div>
                <div className="list-item"><strong>Constraints</strong><p>{context.constraints}</p></div>
              </div>
            ) : (
              <p>Build context after sending a message.</p>
            )}
          </section>

          <section className="panel">
            <h2>Router</h2>
            {route ? (
              <div className="grid">
                <div className="list-item">
                  <strong>{route.title}</strong>
                  <p>{route.reason}</p>
                </div>
                <div className="actions">
                  <Link className="button" href={`/apps/${route.recommended_app}?session=${sessionId}`}>
                    Open mini-app
                  </Link>
                  <Link className="secondary-button" href={`/summary?session=${sessionId}`}>Summary</Link>
                </div>
              </div>
            ) : (
              <p>Run the router to get a recommendation.</p>
            )}
          </section>
        </aside>
      </div>
    </div>
  );
}
