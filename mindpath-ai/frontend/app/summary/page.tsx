"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import RequireAuth from "@/components/RequireAuth";
import { apiRequest, getCurrentSession } from "@/lib/api";
import type { Summary } from "@/lib/types";

export default function SummaryPage() {
  return (
    <RequireAuth>
      <SummaryContent />
    </RequireAuth>
  );
}

function SummaryContent() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const querySession = Number(params.get("session"));
    const sessionId = Number.isFinite(querySession) && querySession > 0 ? querySession : getCurrentSession();
    if (!sessionId) {
      setError("Open a session first.");
      return;
    }
    apiRequest<Summary>(`/summary/${sessionId}`)
      .then(setSummary)
      .catch((err: Error) => setError(err.message));
  }, []);

  const exportText = useMemo(() => {
    if (!summary) {
      return "";
    }
    const lines = [
      "MindPath AI Session Summary",
      `Session: ${summary.session.title}`,
      "",
      "Context:",
      `Problem: ${summary.context?.problem || "No context"}`,
      `Emotion: ${summary.context?.emotion || "No context"}`,
      `Goal: ${summary.context?.goal || "No context"}`,
      `Constraints: ${summary.context?.constraints || "No context"}`,
      `Recommended app: ${summary.context?.recommended_app || "No recommendation"}`,
      "",
      "Mini-app result:",
      summary.latest_result?.result_text || "No mini-app result yet",
      "",
      "Messages:",
      ...summary.messages.map((message) => `${message.role}: ${message.text}`)
    ];
    return lines.join("\n");
  }, [summary]);

  function downloadTxt() {
    const blob = new Blob([exportText], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "mindpath_session_summary.txt";
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="container grid">
      <section className="card">
        <p className="eyebrow">Final summary</p>
        <h1>Session overview</h1>
        <p>Review the saved context, messages, mini-app result, and progress entries.</p>
        <div className="actions">
          <button className="button" type="button" onClick={downloadTxt} disabled={!summary}>
            Export TXT
          </button>
          <Link className="secondary-button" href="/dashboard">Dashboard</Link>
        </div>
        {error && <p className="error">{error}</p>}
      </section>

      {summary && (
        <div className="grid grid-2">
          <section className="panel grid">
            <h2>Context</h2>
            <div className="list-item"><strong>Problem</strong><p>{summary.context?.problem || "No context yet"}</p></div>
            <div className="list-item"><strong>Emotion</strong><p>{summary.context?.emotion || "No context yet"}</p></div>
            <div className="list-item"><strong>Goal</strong><p>{summary.context?.goal || "No context yet"}</p></div>
            <div className="list-item"><strong>Recommended app</strong><p>{summary.context?.recommended_app || "No recommendation yet"}</p></div>
          </section>

          <section className="panel grid">
            <h2>Mini-app result</h2>
            <p>{summary.latest_result?.result_text || "No result saved yet."}</p>
          </section>

          <section className="panel grid">
            <h2>Messages</h2>
            <div className="list">
              {summary.messages.map((message) => (
                <div className="list-item" key={message.id}>
                  <strong>{message.role}</strong>
                  <p>{message.text}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="panel grid">
            <h2>Progress entries for this session</h2>
            <div className="list">
              {summary.progress_entries.map((entry) => (
                <div className="list-item" key={entry.id}>
                  <strong>Mood {entry.mood_score}/10</strong>
                  <p>{entry.note || "No note"}</p>
                </div>
              ))}
              {summary.progress_entries.length === 0 && <p>No progress entries linked to this session yet.</p>}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
