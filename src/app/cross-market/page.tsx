import { CrossMarketTable } from "@/components/cross-market-table";

export const dynamic = "force-dynamic";

export default function CrossMarketPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-50">Cross-Market Arbitrage</h1>
        <p className="text-base text-slate-400 mt-1">
          Compare probabilities across Polymarket, Kalshi, sportsbooks, and crypto markets
        </p>
      </div>
      <div className="h-[720px]">
        <CrossMarketTable />
      </div>
    </div>
  );
}
