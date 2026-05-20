"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { apiRequest, getCurrentSession } from "@/lib/api";
import type { MiniAppDefinition, MiniAppInsight, MiniAppResult } from "@/lib/types";

const localDefinitions: Record<string, MiniAppDefinition> = {
  "problem-analysis": {
    id: "problem-analysis",
    title: "Problem Analysis",
    description: "Structure the main problem and find a first small step.",
    questions: [
      "What is the main problem?",
      "When did it start?",
      "What makes it difficult?",
      "What result would feel helpful?"
    ]
  },
  "anxiety-helper": {
    id: "anxiety-helper",
    title: "Anxiety Helper",
    description: "Balance a worry with facts and choose one safe action.",
    questions: [
      "What exactly are you worried about?",
      "What facts support this worry?",
      "What facts make it less certain?",
      "What is one safe small action today?"
    ]
  },
  "decision-assistant": {
    id: "decision-assistant",
    title: "Decision Assistant",
    description: "Compare options, pros, cons, and the main risk.",
    questions: [
      "What decision do you need to make?",
      "What options do you have?",
      "What are the pros and cons?",
      "What is the main risk?"
    ]
  },
  "goal-planner": {
    id: "goal-planner",
    title: "Goal Planner",
    description: "Turn a goal into a short weekly action plan.",
    questions: [
      "What goal do you want to reach?",
      "Why is it important?",
      "What deadline do you have?",
      "What are 3 small steps?"
    ]
  }
};

export default function MiniAppForm({ appId }: { appId: string }) {
  const fallback = localDefinitions[appId];
  const [app, setApp] = useState<MiniAppDefinition>(fallback);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<MiniAppResult | null>(null);
  const [insight, setInsight] = useState<MiniAppInsight | null>(null);
  const [insightLoading, setInsightLoading] = useState(false);
  const [error, setError] = useState("");

  const summaryLink = useMemo(() => {
    return sessionId ? `/summary?session=${sessionId}` : "/summary";
  }, [sessionId]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const querySession = Number(params.get("session"));
    const savedSession = getCurrentSession();
    const nextSessionId = Number.isFinite(querySession) && querySession > 0 ? querySession : savedSession;
    setSessionId(nextSessionId);

    if (nextSessionId) {
      apiRequest<MiniAppDefinition>(`/mini-apps/${appId}/start`, {
        method: "POST",
        body: JSON.stringify({ session_id: nextSessionId })
      })
        .then(setApp)
        .catch((err: Error) => setError(err.message));
    }
  }, [appId]);

  function updateAnswer(index: number, value: string) {
    setAnswers((current) => ({ ...current, [`q${index + 1}`]: value }));
  }

  async function requestInsight() {
    if (!sessionId) {
      setError("Create or open a session first.");
      return;
    }

    const hasAnswer = Object.values(answers).some((value) => value.trim());
    if (!hasAnswer) {
      setError("Fill in at least one answer to get an AI insight.");
      return;
    }

    setError("");
    setInsightLoading(true);
    try {
      const response = await apiRequest<MiniAppInsight>(`/mini-apps/${appId}/insight`, {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId, answers })
      });
      setInsight(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not get AI insight");
    } finally {
      setInsightLoading(false);
    }
  }

  async function submitAnswers(event: FormEvent) {
    event.preventDefault();
    if (!sessionId) {
      setError("Create or open a session first.");
      return;
    }

    setError("");
    try {
      const saved = await apiRequest<MiniAppResult>(`/mini-apps/${appId}/answer`, {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId, answers })
      });
      setResult(saved);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save mini-app result");
    }
  }

  return (
    <RequireMiniAppLayout title={app.title} description={app.description}>
      {!sessionId && (
        <div className="notice">
          Open this mini-app from a chat session. You can create a new session on the dashboard.
        </div>
      )}

      <form className="form" onSubmit={submitAnswers}>
        {app.questions.map((question, index) => (
          <label key={question}>
            {question}
            <textarea
              rows={3}
              value={answers[`q${index + 1}`] || ""}
              onChange={(event) => updateAnswer(index, event.target.value)}
              required
            />
          </label>
        ))}
        {error && <p className="error">{error}</p>}
        <div className="actions">
          <button
            className="secondary-button"
            type="button"
            onClick={requestInsight}
            disabled={insightLoading}
          >
            {insightLoading ? "Getting insight…" : "Get AI insight"}
          </button>
          <button className="button" type="submit">Save result</button>
          <Link className="secondary-button" href={summaryLink}>Open summary</Link>
        </div>
      </form>

      {insight && (
        <div className="panel">
          <h3>AI insight{insight.llm_used ? "" : " (offline mode)"}</h3>
          <p>{insight.insight}</p>
          <p className="eyebrow">
            Insight is a preview — save the form when you are ready for the final result.
          </p>
        </div>
      )}

      {result && (
        <div className="panel">
          <h3>Saved result</h3>
          <p>{result.result_text}</p>
          <Link className="button" href={summaryLink}>Go to final summary</Link>
        </div>
      )}
    </RequireMiniAppLayout>
  );
}

function RequireMiniAppLayout({
  title,
  description,
  children
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <div className="container grid">
      <div className="card">
        <p className="eyebrow">Mini-app</p>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      <div className="panel grid">{children}</div>
    </div>
  );
}
