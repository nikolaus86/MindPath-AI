# Architecture

MindPath AI uses a simple full-stack architecture.

```text
Browser
  |
  | HTTP with token
  v
Next.js frontend
  |
  | REST API calls
  v
FastAPI backend
  |
  | SQLAlchemy ORM
  v
SQLite database
```

## Components

### Frontend

The frontend is built with Next.js and TypeScript. It uses routed pages instead of placing the whole application on one screen.

Main pages:

- Landing page
- Login/register page
- Dashboard
- Chat
- Session history
- Mini-app catalog
- Four mini-app pages
- Final summary

The frontend stores the access token in localStorage and sends it in the Authorization header.

### Backend

The backend is built with FastAPI. Route files are thin and call service functions. The backend contains services for authentication, sessions, chat, context, routing, mini-apps, summary, and progress.

### Database

SQLite is used for local MVP testing. The database has tables for users, sessions, messages, context files, mini-app results, and progress entries.

## Data flow

1. User registers or logs in.
2. Backend returns a token.
3. User creates a session.
4. User writes chat messages.
5. Backend saves messages.
6. Context service builds a structured context.
7. Router service selects a mini-app.
8. User answers mini-app questions.
9. Mini-app result is saved.
10. Summary service returns a final overview.

## Router logic

The router is deterministic and based on keywords:

- anxiety, worry, stress, panic -> Anxiety Helper
- choose, decision, option, unsure -> Decision Assistant
- goal, plan, improve, habit -> Goal Planner
- default -> Problem Analysis

This approach is simple, defendable, and does not require an external AI API.
