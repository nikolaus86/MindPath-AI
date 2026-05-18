"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { apiRequest, setToken } from "@/lib/api";
import type { User } from "@/lib/types";

type AuthResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("student@example.com");
  const [password, setPassword] = useState("123456");
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const response = await apiRequest<AuthResponse>(`/auth/${mode}`, {
        method: "POST",
        body: JSON.stringify({ email, password })
      });
      setToken(response.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    }
  }

  return (
    <div className="container">
      <section className="hero">
        <div className="card">
          <p className="eyebrow">Account</p>
          <h1>{mode === "login" ? "Log in" : "Register"}</h1>
          <p>
            Create a local account for testing. The backend stores sessions, messages,
            mini-app results, and progress entries in SQLite.
          </p>
        </div>

        <form className="panel form" onSubmit={submit}>
          <div className="actions">
            <button
              className={mode === "login" ? "button" : "secondary-button"}
              type="button"
              onClick={() => setMode("login")}
            >
              Login
            </button>
            <button
              className={mode === "register" ? "button" : "secondary-button"}
              type="button"
              onClick={() => setMode("register")}
            >
              Register
            </button>
          </div>

          <label>
            Email
            <input value={email} onChange={(event) => setEmail(event.target.value)} />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {error && <p className="error">{error}</p>}
          <button className="button" type="submit">
            {mode === "login" ? "Log in" : "Create account"}
          </button>
        </form>
      </section>
    </div>
  );
}
