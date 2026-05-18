# API Documentation

Base URL for local development:

```text
http://localhost:8000
```

Protected endpoints require:

```text
Authorization: Bearer <token>
```

## Auth

### POST /auth/register

Request:

```json
{
  "email": "student@example.com",
  "password": "123456"
}
```

Response:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "student@example.com",
    "created_at": "..."
  }
}
```

### POST /auth/login

Request:

```json
{
  "email": "student@example.com",
  "password": "123456"
}
```

### GET /auth/me

Returns the current authenticated user.

## Sessions

### POST /sessions

Creates a new reflection session.

Request:

```json
{
  "title": "Study decision"
}
```

### GET /sessions

Returns all sessions for the current user.

### GET /sessions/{session_id}

Returns one session owned by the current user.

### DELETE /sessions/{session_id}

Deletes a session and its related data.

## Chat

### POST /chat/{session_id}/messages

Request:

```json
{
  "text": "I feel worried about choosing my study plan."
}
```

The backend saves the user message and a small assistant response.

### GET /chat/{session_id}/messages

Returns saved chat messages for a session.

## Context

### POST /context/{session_id}/build

Builds and saves a structured context from user messages.

### GET /context/{session_id}

Returns the latest saved context for the session.

## Router

### POST /router/{session_id}/route

Runs deterministic routing and saves the recommended mini-app.

## Mini-apps

### GET /mini-apps

Returns all available mini-app definitions.

### POST /mini-apps/{app_id}/start

Request:

```json
{
  "session_id": 1
}
```

Returns selected mini-app questions.

### POST /mini-apps/{app_id}/answer

Request:

```json
{
  "session_id": 1,
  "answers": {
    "q1": "...",
    "q2": "..."
  }
}
```

Saves the answers and returns the generated result text.

### GET /mini-apps/{session_id}/results

Returns mini-app results for the session.

## Summary

### GET /summary/{session_id}

Returns session, messages, context, latest mini-app result, and progress information.

## Progress

### POST /progress

Request:

```json
{
  "session_id": 1,
  "mood_score": 7,
  "note": "I feel more clear after making a plan."
}
```

### GET /progress

Returns progress entries and the average mood score.
