import RequireAuth from "@/components/RequireAuth";
import MiniAppForm from "@/components/MiniAppForm";

export default function AnxietyHelperPage() {
  return (
    <RequireAuth>
      <MiniAppForm appId="anxiety-helper" />
    </RequireAuth>
  );
}
