"use client";

import { useCrossMarket } from "@/hooks/use-cross-market";
import { formatProbability, formatVolume } from "@/lib/data";
import { ClientTime } from "@/components/client-time";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { GitCompare, AlertTriangle } from "lucide-react";

export function CrossMarketTable() {
  const { comparisons, loading, usingMock, error } = useCrossMarket();

  if (loading && comparisons.length === 0) {
    return (
      <Card className="border-slate-800 bg-slate-950">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold text-slate-100">Cross-Market Arbitrage</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-12">
          <p className="text-sm text-slate-500">Loading cross-market data...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-slate-800 bg-slate-950">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GitCompare className="h-4 w-4 text-emerald-400" />
            <CardTitle className="text-sm font-semibold text-slate-100">
              Cross-Market Arbitrage
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
            <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px]">
              {comparisons.length} Events
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && comparisons.length === 0 && (
          <div className="rounded-lg border border-rose-800 bg-rose-950/20 p-4">
            <p className="text-xs text-rose-300">Failed to load cross-market data. Check browser console for details.</p>
          </div>
        )}
        {comparisons.map((comp, i) => {
          const maxProb = Math.max(...comp.markets.map((m) => m.probability));
          const minProb = Math.min(...comp.markets.map((m) => m.probability));
          return (
            <div
              key={i}
              className="rounded-lg border border-slate-800 bg-slate-900/50 p-4"
            >
              <div className="flex items-start justify-between gap-4 mb-3">
                <div>
                  <p className="text-sm font-medium text-slate-200">
                    {comp.event_title}
                  </p>
                  {comp.arbitrage_hint && (
                    <div className="mt-1 flex items-center gap-1.5 text-[10px] text-amber-400">
                      <AlertTriangle className="h-3 w-3" />
                      {comp.arbitrage_hint}
                    </div>
                  )}
                </div>
                <Badge
                  variant="outline"
                  className={`text-[10px] ${
                    comp.disagreement_score > 0.15
                      ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                      : "bg-slate-500/10 text-slate-400 border-slate-500/20"
                  }`}
                >
                  Δ {(comp.disagreement_score * 100).toFixed(0)}pts
                </Badge>
              </div>

              <div className="space-y-2">
                {comp.markets.map((m, j) => (
                  <div
                    key={j}
                    className="flex items-center gap-3 rounded-md bg-slate-950 px-3 py-2"
                  >
                    <span className="min-w-[100px] text-xs font-medium text-slate-300">
                      {m.source}
                    </span>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <div className="h-2 flex-1 rounded-full bg-slate-800 overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all ${
                              m.probability === maxProb
                                ? "bg-emerald-500"
                                : m.probability === minProb
                                ? "bg-rose-500"
                                : "bg-slate-500"
                            }`}
                            style={{ width: `${m.probability * 100}%` }}
                          />
                        </div>
                        <span className="min-w-[40px] text-right text-xs font-bold text-slate-200">
                          {formatProbability(m.probability)}
                        </span>
                      </div>
                    </div>
                    <span className="min-w-[60px] text-right text-[10px] text-slate-500">
                      {m.volume > 0 ? formatVolume(m.volume) : "—"}
                    </span>
                    <span className="min-w-[50px] text-right">
                      <ClientTime iso={m.updated_at} />
                    </span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
