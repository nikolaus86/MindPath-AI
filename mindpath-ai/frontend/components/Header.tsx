"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { clearToken, getToken } from "@/lib/api";
import ThemeToggle from "./ThemeToggle";

export default function Header() {
  const router = useRouter();

  function logout() {
    clearToken();
    router.push("/login");
  }

  return (
    <header className="header">
      <div className="container header-inner">
        <Link href="/" className="logo">
          <span className="logo-mark">M</span>
          <span>MindPath AI</span>
        </Link>
        <nav className="nav">
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/chat">Chat</Link>
          <Link href="/sessions">Sessions</Link>
          <Link href="/apps">Mini-apps</Link>
          <ThemeToggle />
          <button type="button" onClick={logout}>Logout</button>
        </nav>
      </div>
    </header>
  );
}
