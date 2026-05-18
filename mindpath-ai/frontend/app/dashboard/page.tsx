"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import MoodTracker from "@/components/MoodTracker";
import RequireAuth from "@/components/RequireAuth";
import { apiRequest, saveCurrentSession } from "@/lib/api";
import type { Session, User } from "@/lib/types";

export default function DashboardPage() {
  return (
    <RequireAuth>
      <DashboardContent />
    </RequireAuth>
  );
}

function DashboardContent() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [error, setError] = useState("");

  async function loadData() {
    const [me, loadedSessions] = await Promise.all([
      apiRequest<User>("/auth/me"),
      apiRequest<Session[]>("/sessions")
    ]);
    setUser(me);
    setSessions(loadedSessions);
  }

  useEffect(() => {
    loadData().catch((err: Error) => setError(err.message));
  }, []);

  async function createSession() {
    setError("");
    try {
      const session = await apiRequest<Session>("/sessions", {
        method: "POST",
        body: JSON.stringify({ title: "New reflection" })
      });
      saveCurrentSession(session.id);
      router.push(`/chat?session=${session.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create session");
    }
  }

  return (
    <div className="container grid">
      <section className="card">
        <p className="eyebrow">Dashboard</p>
        <h1>Welcome{user ? `, ${user.email}` : ""}</h1>
        <p>Create a session, continue previous work, or add a simple progress note.</p>
        <div className="actions">
          <button className="button" type="button" onClick={createSession}>New session</button>
          <Link className="secondary-button" href="/sessions">Session history</Link>
          <Link className="secondary-button" href="/apps">Mini-app catalog</Link>
        </div>
        {error && <p className="error">{error}</p>}
      </section>

      <div className="grid grid-2">
        <section className="panel grid">
          <h2>Latest sessions</h2>
          <div className="list">
            {sessions.slice(0, 4).map((session) => (
              <Link
                className="list-item"
                key={session.id}
                href={`/chat?session=${session.id}`}
                onClick={() => saveCurrentSession(session.id)}
              >
                <strong>{session.title}</strong>
                <p>Updated: {new Date(session.updated_at).toLocaleString()}</p>
              </Link>
            ))}
            {sessions.length === 0 && <p>No sessions yet.</p>}
          </div>
        </section>
        <MoodTracker />
      </div>
    </div>
  );
}
