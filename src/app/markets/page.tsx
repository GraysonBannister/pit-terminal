import { MarketList } from "@/components/market-list";

export default function MarketsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-50">Markets</h1>
        <p className="text-base text-slate-400 mt-1">
          Active prediction markets tracked by the terminal
        </p>
      </div>
      <div className="h-[720px]">
        <MarketList />
      </div>
    </div>
  );
}
