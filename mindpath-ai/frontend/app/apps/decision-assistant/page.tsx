import RequireAuth from "@/components/RequireAuth";
import MiniAppForm from "@/components/MiniAppForm";

export default function DecisionAssistantPage() {
  return (
    <RequireAuth>
      <MiniAppForm appId="decision-assistant" />
    </RequireAuth>
  );
}
