import RequireAuth from "@/components/RequireAuth";
import MiniAppForm from "@/components/MiniAppForm";

export default function GoalPlannerPage() {
  return (
    <RequireAuth>
      <MiniAppForm appId="goal-planner" />
    </RequireAuth>
  );
}
