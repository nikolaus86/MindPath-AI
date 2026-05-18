import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="container">
      <section className="hero">
        <div className="card">
          <p className="eyebrow">Self-reflection MVP</p>
          <h1>MindPath AI</h1>
          <p>
            A simple web app that helps users describe a personal problem, build structured
            context, get routed to a focused mini-app, and save a small result or plan.
          </p>
          <div className="actions">
            <Link className="button" href="/login">Start</Link>
            <Link className="secondary-button" href="/apps">View mini-apps</Link>
          </div>
        </div>

        <div className="panel grid">
          <h2>How it works</h2>
          <div className="list">
            <div className="list-item"><strong>1. Chat</strong><p>Describe the situation in your own words.</p></div>
            <div className="list-item"><strong>2. Context</strong><p>The backend saves a structured context for the session.</p></div>
            <div className="list-item"><strong>3. Router</strong><p>A deterministic router recommends one mini-app.</p></div>
            <div className="list-item"><strong>4. Summary</strong><p>The final page collects messages, context, and result.</p></div>
          </div>
        </div>
      </section>

      <div className="footer-space" />

      <section className="notice">
        MindPath AI is not a replacement for professional therapy, medical advice, or emergency help.
        It is a student MVP for guided self-reflection and planning.
      </section>
    </div>
  );
}
