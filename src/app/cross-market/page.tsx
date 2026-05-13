import { CrossMarketTable } from "@/components/cross-market-table";

export default function CrossMarketPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-100">Cross-Market Arbitrage</h1>
        <p className="text-sm text-slate-400">
          Compare probabilities across Polymarket, Kalshi, sportsbooks, and crypto markets.
        </p>
      </div>
      <div className="h-[720px]">
        <CrossMarketTable />
      </div>
    </div>
  );
}
