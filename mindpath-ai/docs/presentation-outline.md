# Presentation Outline: 12 Slides

## 1. Title

MindPath AI: Self-Reflection Assistant

Include team name, course, and date.

## 2. Problem

Many users have personal doubts, stress, or decisions, but they do not know how to structure the problem. They need a simple first step before deeper work.

## 3. Solution

MindPath AI offers a guided flow: chat, context building, routing to a mini-app, and final summary.

## 4. User flow

Landing page -> Login/register -> Dashboard -> Chat -> Router recommendation -> Mini-app -> Summary.

## 5. Architecture

Show three main layers: Next.js frontend, FastAPI backend, SQLite database.

## 6. Backend

Explain routers, services, models, authentication, sessions, and database persistence.

## 7. Frontend

Explain routed pages, dashboard, chat, session history, mini-app pages, summary, and theme toggle.

## 8. Database

Show tables: users, sessions, messages, context_files, mini_app_results, progress_entries.

## 9. Mini-apps

Explain four mini-apps: Problem Analysis, Anxiety Helper, Decision Assistant, Goal Planner.

## 10. Additional features

Explain TXT export, light/dark theme toggle, and mood/progress tracker.

## 11. Demo scenario

Use one example: the user feels stressed about choosing a study direction. Show how the router recommends a mini-app and how the summary is generated.

## 12. Limitations and next steps

Limitations: no medical diagnosis, no real ML model, SQLite only for MVP, no complex charts. Next steps: better context analysis, richer UI, team accounts, and more detailed progress reports.
