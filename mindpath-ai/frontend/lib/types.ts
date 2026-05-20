export type User = {
  id: number;
  email: string;
  created_at: string;
};

export type Session = {
  id: number;
  user_id: number;
  title: string;
  created_at: string;
  updated_at: string;
};

export type Message = {
  id: number;
  session_id: number;
  role: "user" | "assistant";
  text: string;
  created_at: string;
};

export type ContextFile = {
  id: number;
  session_id: number;
  problem: string;
  emotion: string;
  goal: string;
  constraints: string;
  summary: string;
  recommended_app: string | null;
  created_at: string;
};

export type MiniAppDefinition = {
  id: string;
  title: string;
  description: string;
  questions: string[];
};

export type MiniAppInsight = {
  insight: string;
  llm_used: boolean;
};

export type MiniAppResult = {
  id: number;
  session_id: number;
  app_id: string;
  answers_json: string;
  result_text: string;
  created_at: string;
};

export type ProgressEntry = {
  id: number;
  user_id: number;
  session_id: number | null;
  mood_score: number;
  note: string;
  created_at: string;
};

export type ProgressList = {
  entries: ProgressEntry[];
  average_mood: number | null;
};

export type Summary = {
  session: Session;
  context: ContextFile | null;
  messages: Message[];
  mini_app_results: MiniAppResult[];
  latest_result: MiniAppResult | null;
  progress_entries: ProgressEntry[];
};
