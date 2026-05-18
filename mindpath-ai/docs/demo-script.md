# Demo Script

## 1. What problem the project solves

MindPath AI helps a user start working with a personal problem when they do not know how to structure it. The app does not diagnose or replace therapy. It gives a simple guided reflection flow.

## 2. How the frontend communicates with the backend

The frontend is built with Next.js. It sends REST API requests to the FastAPI backend. After login, the frontend saves a token in localStorage and sends it in the Authorization header.

## 3. How sessions work

Each user can create several sessions. A session is one reflection case. Messages, context, mini-app results, and some progress notes can be connected to the session.

During the demo, I create a new session from the dashboard and open the chat page.

## 4. How context is built

The user writes a message in the chat. The backend saves this message in the messages table. Then the context service reads the user messages and creates a context file with problem, emotion, goal, constraints, and summary.

This context is saved in the context_files table.

## 5. How the router selects a mini-app

The router uses deterministic keyword rules. For example, if the message contains words like anxiety, worry, stress, or panic, the backend recommends the Anxiety Helper. If the message contains choose, decision, option, or unsure, it recommends the Decision Assistant. If the message contains goal, plan, improve, or habit, it recommends the Goal Planner. Otherwise, it recommends Problem Analysis.

This is simple, transparent, and easy to explain during the defense.

## 6. How the mini-app saves result

The user opens the recommended mini-app and answers four questions. The frontend sends the answers to the backend. The mini-app service creates a small result text and saves it in the mini_app_results table.

## 7. What additional features were added

There are two small features:

- The summary page can export the session summary as a TXT file.
- The interface has a light/dark theme toggle saved in localStorage.

There is also one medium feature:

- A mood/progress tracker. The user can enter a mood score from 1 to 10 and a short note. The dashboard shows latest entries and average mood.

## 8. What limitations exist

The app uses rule-based routing, not a real ML model. SQLite is used for local testing. The app is not a medical tool and does not replace professional support. There are no complex charts, payment features, or external API integrations.

## 9. Suggested live demo

1. Open the landing page.
2. Register a new account.
3. Open the dashboard.
4. Add one mood entry.
5. Create a new session.
6. Write: `I feel worried and stressed about choosing my study direction.`
7. Build context.
8. Run the router.
9. Open the recommended mini-app.
10. Answer all questions.
11. Open the summary page.
12. Export the summary as TXT.
