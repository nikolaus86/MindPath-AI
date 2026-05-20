# MindPath AI

MindPath AI is a full-stack self-reflection web application. It helps a user describe a personal problem, creates a structured context, routes the session to a suitable mini-app, and saves a small result or action plan.

The project is built as a student MVP for an exam defense. Chat, context, routing, and mini-app results can use **Groq** or **Google Gemini** when an API key is configured. Without a key or when the API fails, the app falls back to simple rule-based text.

MindPath AI is not a replacement for professional therapy, medical advice, or emergency support. It is only a self-reflection and planning tool.

## Features

- Landing page with project explanation.
- Register, login, and token-based authentication.
- Dashboard with session access and mood/progress tracker.
- Main chat with saved messages.
- Context builder that extracts problem, emotion, goal, constraints, and summary.
- LLM-powered chat, context, router, and mini-apps via Groq or Gemini (with rule-based fallback).
- Mini-app catalog with four working tools:
  - Problem Analysis
  - Anxiety Helper
  - Decision Assistant
  - Goal Planner
- Final summary page with saved context, mini-app result, and progress data.
- TXT export from the summary page.
- Light/dark theme toggle saved in localStorage.
- SQLite persistence for local testing.

## Architecture

The project has two main parts:

```text
Next.js frontend  ->  FastAPI backend  ->  SQLite database
```

The frontend sends authenticated HTTP requests to the backend. The backend stores users, sessions, messages, context files, mini-app results, and progress entries. Business logic is placed in service modules, while route files stay small.

## Stack

Frontend:

- Next.js
- TypeScript
- React
- Simple CSS

Backend:

- FastAPI
- Python
- SQLAlchemy
- Pydantic
- SQLite
- Token-based authentication

## How to run on Ubuntu

Open two terminal windows.

### Backend

Copy `backend/.env.example` to `backend/.env` and set an LLM API key.

**Groq** (recommended if Gemini quota is limited) — [console.groq.com](https://console.groq.com/keys):

```bash
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
```

**Gemini** — [Google AI Studio](https://aistudio.google.com/apikey):

```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
```

With `LLM_PROVIDER=auto` (default), Groq is used when `GROQ_API_KEY` is set, otherwise Gemini.

Check config: open `http://localhost:8000/` — expect `"llm_configured": true` and `"llm_provider": "groq"` or `"gemini"`.

```bash
cd mindpath-ai/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Docker Compose

```bash
cd mindpath-ai
docker compose up
```

The backend service loads `backend/.env` automatically. Restart after changing the key: `docker compose restart backend`.

The backend runs on:

```text
http://localhost:8000
```

FastAPI documentation opens at:

```text
http://localhost:8000/docs
```

### Frontend

```bash
cd mindpath-ai/frontend
npm install
npm run dev
```

Then open:

```text
http://localhost:3000
```

### Frontend production build

```bash
cd mindpath-ai/frontend
npm install
npm run build
npm start
```

## Demo user flow

1. Open the landing page.
2. Go to Login/Register.
3. Create a user account.
4. Open the dashboard.
5. Create a new reflection session.
6. Write a message in the chat, for example: `I feel stressed and worried about choosing my next study plan.`
7. Build context and ask the router for a recommendation.
8. Open the recommended mini-app.
9. Answer the mini-app questions.
10. Open the final summary.
11. Export the summary as a TXT file.
12. Add a mood/progress entry on the dashboard.

## API overview

Authentication:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

Sessions:

- `POST /sessions`
- `GET /sessions`
- `GET /sessions/{session_id}`
- `DELETE /sessions/{session_id}`

Chat:

- `POST /chat/{session_id}/messages`
- `GET /chat/{session_id}/messages`

Context:

- `POST /context/{session_id}/build`
- `GET /context/{session_id}`

Router:

- `POST /router/{session_id}/route`

Mini-apps:

- `GET /mini-apps`
- `POST /mini-apps/{app_id}/start`
- `POST /mini-apps/{app_id}/answer`
- `GET /mini-apps/{session_id}/results`

Summary:

- `GET /summary/{session_id}`

Progress:

- `POST /progress`
- `GET /progress`

## Project structure

```text
mindpath-ai/
  frontend/
    app/
    components/
    lib/
  backend/
    app/
      routers/
      services/
  docs/
  README.md
  docker-compose.yml
  .gitignore
```

## Team-defense explanation

The project demonstrates a complete MVP flow. The user logs in, creates a session, writes a message, and the backend stores the conversation. The context service builds a structured context from user messages. The router service uses clear keyword rules to select a mini-app. The mini-app service saves answers and produces a simple result. The final summary combines the saved session data into one page.

This structure is easy to defend because every part has a clear role:

- frontend pages handle navigation and user interaction;
- backend routers receive API requests;
- services contain business logic;
- models define database tables;
- SQLite stores local data.

## Limitations

- The router uses deterministic keyword rules, not a real machine learning model.
- The app does not provide medical diagnosis or therapy.
- The local SQLite database is suitable for MVP testing, not for production scale.
- There is no password reset flow.
- There is no team admin panel.
- There are no complex charts for progress tracking.

## Optional Docker run

Normal local run is recommended for the defense. Docker Compose is included only as an optional helper:

```bash
docker compose up --build
```
