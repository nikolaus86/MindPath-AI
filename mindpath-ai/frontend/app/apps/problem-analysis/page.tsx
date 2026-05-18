import RequireAuth from "@/components/RequireAuth";
import MiniAppForm from "@/components/MiniAppForm";

export default function ProblemAnalysisPage() {
  return (
    <RequireAuth>
      <MiniAppForm appId="problem-analysis" />
    </RequireAuth>
  );
}
