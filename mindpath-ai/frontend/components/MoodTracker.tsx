"use client";

import { FormEvent, useEffect, useState } from "react";
import { apiRequest } from "@/lib/api";
import type { ProgressList } from "@/lib/types";

export default function MoodTracker() {
  const [moodScore, setMoodScore] = useState(7);
  const [note, setNote] = useState("");
  const [progress, setProgress] = useState<ProgressList>({ entries: [], average_mood: null });
  const [error, setError] = useState("");

  async function loadProgress() {
    const data = await apiRequest<ProgressList>("/progress");
    setProgress(data);
  }

  useEffect(() => {
    loadProgress().catch((err: Error) => setError(err.message));
  }, []);

  async function submitProgress(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await apiRequest("/progress", {
        method: "POST",
        body: JSON.stringify({ mood_score: moodScore, note })
      });
      setNote("");
      await loadProgress();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save progress");
    }
  }

  return (
    <section className="panel grid">
      <div>
        <p className="eyebrow">Progress tracker</p>
        <h2>Mood and notes</h2>
        <p>Save a simple mood score and a short note. This is only for self-reflection.</p>
      </div>

      <div className="grid grid-2">
        <div className="kpi">
          <span>Average mood</span>
          <strong>{progress.average_mood ?? "—"}</strong>
        </div>
        <div className="kpi">
          <span>Total entries</span>
          <strong>{progress.entries.length}</strong>
        </div>
      </div>

      <form className="form" onSubmit={submitProgress}>
        <label>
          Mood score: {moodScore}
          <input
            type="range"
            min="1"
            max="10"
            value={moodScore}
            onChange={(event) => setMoodScore(Number(event.target.value))}
          />
        </label>
        <label>
          Note
          <textarea
            rows={3}
            value={note}
            onChange={(event) => setNote(event.target.value)}
            placeholder="Short note about today"
          />
        </label>
        {error && <p className="error">{error}</p>}
        <div>
          <button className="button" type="submit">Save progress</button>
        </div>
      </form>

      <div className="list">
        {progress.entries.slice(0, 5).map((entry) => (
          <div className="list-item" key={entry.id}>
            <strong>Mood {entry.mood_score}/10</strong>
            <p>{entry.note || "No note"}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
