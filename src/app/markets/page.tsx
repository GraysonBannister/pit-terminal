import { MarketList } from "@/components/market-list";

export default function MarketsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-100">Markets</h1>
        <p className="text-sm text-slate-400">
          Active prediction markets tracked by the terminal.
        </p>
      </div>
      <div className="h-[720px]">
        <MarketList />
      </div>
    </div>
  );
}
