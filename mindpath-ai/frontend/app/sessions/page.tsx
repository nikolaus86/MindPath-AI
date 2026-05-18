"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import RequireAuth from "@/components/RequireAuth";
import { apiRequest, saveCurrentSession } from "@/lib/api";
import type { Session } from "@/lib/types";

export default function SessionsPage() {
  return (
    <RequireAuth>
      <SessionsContent />
    </RequireAuth>
  );
}

function SessionsContent() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [error, setError] = useState("");

  async function loadSessions() {
    const data = await apiRequest<Session[]>("/sessions");
    setSessions(data);
  }

  useEffect(() => {
    loadSessions().catch((err: Error) => setError(err.message));
  }, []);

  async function deleteSession(sessionId: number) {
    setError("");
    try {
      await apiRequest(`/sessions/${sessionId}`, { method: "DELETE" });
      await loadSessions();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete session");
    }
  }

  return (
    <div className="container grid">
      <section className="card">
        <p className="eyebrow">Session history</p>
        <h1>Previous sessions</h1>
        <p>Open an older session, continue in chat, or remove it.</p>
        {error && <p className="error">{error}</p>}
      </section>

      <section className="panel list">
        {sessions.map((session) => (
          <div className="list-item" key={session.id}>
            <h3>{session.title}</h3>
            <p>Created: {new Date(session.created_at).toLocaleString()}</p>
            <p>Updated: {new Date(session.updated_at).toLocaleString()}</p>
            <div className="actions">
              <Link
                className="button"
                href={`/chat?session=${session.id}`}
                onClick={() => saveCurrentSession(session.id)}
              >
                Open chat
              </Link>
              <Link
                className="secondary-button"
                href={`/summary?session=${session.id}`}
                onClick={() => saveCurrentSession(session.id)}
              >
                Summary
              </Link>
              <button className="danger-button" type="button" onClick={() => deleteSession(session.id)}>
                Delete
              </button>
            </div>
          </div>
        ))}
        {sessions.length === 0 && <p>No saved sessions yet.</p>}
      </section>
    </div>
  );
}
