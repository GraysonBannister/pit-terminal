import { OpportunityFeed } from "@/components/opportunity-feed";

export const dynamic = "force-dynamic";

export default function OpportunitiesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-50">Opportunities</h1>
        <p className="text-base text-slate-400 mt-1">
          Potentially mispriced markets ranked by confidence score
        </p>
      </div>
      <div className="h-[720px]">
        <OpportunityFeed />
      </div>
    </div>
  );
}
