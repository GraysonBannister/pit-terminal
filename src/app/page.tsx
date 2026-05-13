import { OpportunityFeed } from "@/components/opportunity-feed";
import { NarrativeTracker } from "@/components/narrative-tracker";
import { CrossMarketTable } from "@/components/cross-market-table";
import { MarketList } from "@/components/market-list";

export const dynamic = "force-dynamic";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-50">Dashboard</h1>
        <p className="text-base text-slate-400 mt-1">
          Live probability intelligence feed and market monitoring
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="h-[520px]">
          <OpportunityFeed />
        </div>
        <div className="h-[520px]">
          <NarrativeTracker />
        </div>
      </div>

      <div className="max-h-[600px]">
        <CrossMarketTable />
      </div>

      <div className="h-[520px]">
        <MarketList />
      </div>
    </div>
  );
}
