# User Stories

## 1. Start using the app

As a user, I want to open the landing page and understand the goal of the product, so that I know whether I want to try it.

Acceptance criteria:

- The user sees the project name.
- The user sees a short explanation.
- The user sees a notice that the app is not a replacement for professional therapy.
- The user can go to login/register.

## 2. Create an account

As a user, I want to register and log in, so that my sessions can be saved.

Acceptance criteria:

- The user can create an account with email and password.
- The user can log in.
- The token is saved in the browser.
- Protected pages can load user data.

## 3. Create a reflection session

As a user, I want to create a session, so that my problem discussion is saved separately.

Acceptance criteria:

- The user can create a new session.
- The user can open previous sessions.
- The user can delete a session.

## 4. Describe a problem in chat

As a user, I want to write messages in a chat, so that I can describe my situation naturally.

Acceptance criteria:

- The user can send a message.
- The message is saved in the database.
- The assistant returns a simple guiding response.

## 5. Build context

As a system, I want to build context from user messages, so that the router can make a useful recommendation.

Acceptance criteria:

- The system identifies a problem.
- The system identifies an emotion.
- The system identifies a goal.
- The context is saved.

## 6. Route to a mini-app

As a user, I want the app to recommend a suitable mini-app, so that I can continue with guided questions.

Acceptance criteria:

- The router selects one of four mini-apps.
- The selected app is saved in the context.
- The user can open the recommended app.

## 7. Complete a mini-app

As a user, I want to answer short guided questions, so that I receive a small result or plan.

Acceptance criteria:

- The mini-app has real questions.
- The answers are saved.
- The result text is generated and saved.

## 8. See final summary

As a user, I want to see all important information in one summary, so that I can review my reflection session.

Acceptance criteria:

- Summary includes session, context, messages, and mini-app result.
- User can export the summary as TXT.

## 9. Track mood and progress

As a user, I want to save mood notes, so that I can see simple progress over time.

Acceptance criteria:

- User enters mood score from 1 to 10.
- User enters a note.
- Dashboard shows latest entries.
- Dashboard shows average mood.
