import { NarrativeTracker } from "@/components/narrative-tracker";

export const dynamic = "force-dynamic";

export default function NarrativesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-50">Narrative Shifts</h1>
        <p className="text-base text-slate-400 mt-1">
          Tracking sentiment changes, attention spikes, and emerging narratives
        </p>
      </div>
      <div className="h-[720px]">
        <NarrativeTracker />
      </div>
    </div>
  );
}
