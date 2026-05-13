import { OpportunityFeed } from "@/components/opportunity-feed";

export default function OpportunitiesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-100">Opportunities</h1>
        <p className="text-sm text-slate-400">
          Potentially mispriced markets ranked by confidence score.
        </p>
      </div>
      <div className="h-[720px]">
        <OpportunityFeed />
      </div>
    </div>
  );
}
