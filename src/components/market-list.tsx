"use client";

import { useMarkets } from "@/hooks/use-markets";
import { formatProbability, formatVolume, getCategoryColor } from "@/lib/data";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { TrendingUp, TrendingDown, Minus, LineChart } from "lucide-react";
import Link from "next/link";

export function MarketList() {
  const { markets, loading, usingMock, error } = useMarkets();

  if (loading && markets.length === 0) {
    return (
      <Card className="border-slate-800 bg-slate-950 h-full flex flex-col">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold text-slate-100">Active Markets</CardTitle>
        </CardHeader>
        <div className="flex-1 flex items-center justify-center">
          <p className="text-sm text-slate-500">Loading markets...</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="border-slate-800 bg-slate-950 h-full flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <LineChart className="h-4 w-4 text-slate-400" />
            <CardTitle className="text-base font-bold text-slate-50">
              Active Markets
            </CardTitle>
          </div>
          <div className="flex items-center gap-2">
            {usingMock && (
              <Badge variant="outline" className="text-[10px] text-rose-400 border-rose-500/30 bg-rose-500/10">
                DEMO DATA
              </Badge>
            )}
            {error && (
              <Badge variant="outline" className="text-[10px] text-rose-400 border-rose-500/30 bg-rose-500/10">
                API Error
              </Badge>
            )}
            <Badge className="bg-slate-500/10 text-slate-400 border-slate-500/20 text-[10px]">
              {markets.length} Markets
            </Badge>
          </div>
        </div>
      </CardHeader>
      <ScrollArea className="flex-1 px-4 pb-4 overflow-y-auto">
        {error && markets.length === 0 && (
          <div className="rounded-lg border border-rose-800 bg-rose-950/20 p-4 mb-4">
            <p className="text-xs text-rose-300">Failed to load markets. Check browser console for details.</p>
          </div>
        )}
        <div className="space-y-2">
          {markets.map((market) => (
            <Link
              key={market.id}
              href={`/market/${market.id}`}
              className="block rounded-lg border border-slate-800 bg-slate-900/50 p-3 transition-colors hover:border-slate-700"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge
                      variant="outline"
                      className={`text-xs uppercase tracking-wide ${getCategoryColor(market.category)}`}
                    >
                      {market.category}
                    </Badge>
                    <span className="text-sm text-slate-400">
                      {market.source}
                    </span>
                  </div>
                  <p className="text-base font-medium text-slate-100 truncate leading-snug">
                    {market.title}
                  </p>
                </div>
                <div className="flex flex-col items-end gap-1.5">
                  <span className="text-lg font-bold text-slate-50">
                    {formatProbability(market.probability)}
                  </span>
                  <div className="flex items-center gap-1.5">
                    {market.recent_movement > 0 ? (
                      <TrendingUp className="h-4 w-4 text-emerald-400" />
                    ) : market.recent_movement < 0 ? (
                      <TrendingDown className="h-4 w-4 text-rose-400" />
                    ) : (
                      <Minus className="h-4 w-4 text-slate-500" />
                    )}
                    <span
                      className={`text-sm font-semibold ${
                        market.recent_movement > 0
                          ? "text-emerald-400"
                          : market.recent_movement < 0
                          ? "text-rose-400"
                          : "text-slate-500"
                      }`}
                    >
                      {market.recent_movement > 0 ? "+" : ""}
                      {(market.recent_movement * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
              <div className="mt-3 flex items-center gap-6 text-sm text-slate-400">
                <span className="font-medium">Vol: <span className="text-slate-300">{formatVolume(market.volume)}</span></span>
                <span className="font-medium">Liq: <span className="text-slate-300">{formatVolume(market.liquidity)}</span></span>
                <span className="font-medium">Spread: <span className="text-slate-300">{(market.spread * 100).toFixed(1)}%</span></span>
                <span className="ml-auto font-medium">
                  Resolves <span className="text-slate-300">{market.resolution_date || "TBD"}</span>
                </span>
              </div>
            </Link>
          ))}
        </div>
      </ScrollArea>
    </Card>
  );
}
