"use client";

import { useOpportunities } from "@/hooks/use-opportunities";
import { formatProbability } from "@/lib/data";
import { getCategoryColor } from "@/lib/data";
import type { ApiOpportunity } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ArrowDown, ArrowUp, TrendingUp, Zap, Newspaper, GitCompare, Droplets, MessageSquare } from "lucide-react";
import Link from "next/link";

const signalIcons: Record<string, React.ReactNode> = {
  news: <Newspaper className="h-3 w-3" />,
  sentiment: <TrendingUp className="h-3 w-3" />,
  cross_market: <GitCompare className="h-3 w-3" />,
  liquidity: <Droplets className="h-3 w-3" />,
  narrative: <MessageSquare className="h-3 w-3" />,
};

function OpportunityCard({ opp }: { opp: ApiOpportunity }) {
  const low = opp.ai_estimated_low;
  const high = opp.ai_estimated_high;
  const divergence = `Market ${formatProbability(opp.market_probability)} vs AI ${formatProbability(low)}–${formatProbability(high)}`;

  return (
    <Card className="border-slate-800 bg-slate-900/50 transition-colors hover:border-slate-700">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 mb-1">
              <Badge
                variant="outline"
                className={`text-xs uppercase tracking-wide ${getCategoryColor(opp.category)}`}
              >
                {opp.category}
              </Badge>
              <span className="text-sm text-slate-400">
                {new Date(opp.created_at).toLocaleTimeString()}
              </span>
            </div>
            <Link
              href={`/market/${opp.market_id}`}
              className="block text-base font-semibold text-slate-100 hover:text-indigo-300 truncate leading-snug"
            >
              {opp.market_title}
            </Link>
            <p className="mt-2 text-sm text-slate-400">{divergence}</p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <div className="flex items-center gap-2">
              {opp.divergence_type === "undervalued" ? (
                <ArrowUp className="h-5 w-5 text-emerald-400" />
              ) : (
                <ArrowDown className="h-5 w-5 text-rose-400" />
              )}
              <span
                className={`text-base font-bold ${
                  opp.divergence_type === "undervalued"
                    ? "text-emerald-400"
                    : "text-rose-400"
                }`}
              >
                {opp.divergence_type === "undervalued" ? "Undervalued" : "Overvalued"}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-slate-400">Confidence</span>
              <span className="text-base font-bold text-indigo-300">
                {opp.confidence_score.toFixed(0)}
              </span>
            </div>
          </div>
        </div>

        <div className="mt-3">
          <Progress value={opp.confidence_score} className="h-1.5 bg-slate-800" />
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {(opp.signals || []).map((signal: { type: string; label: string; strength: number }, i: number) => (
            <div
              key={i}
              className="flex items-center gap-2 rounded-md border border-slate-700 bg-slate-950 px-3 py-1.5"
            >
              <span className="text-slate-400">{signalIcons[signal.type] || <TrendingUp className="h-4 w-4" />}</span>
              <span className="text-sm font-medium text-slate-300">
                {signal.label}
              </span>
              <span className="text-sm font-semibold text-slate-500">
                {(signal.strength * 100).toFixed(0)}%
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export function OpportunityFeed() {
  const { opportunities, loading, usingMock, error } = useOpportunities();

  if (loading && opportunities.length === 0) {
    return (
      <Card className="border-slate-800 bg-slate-950 h-full flex flex-col">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold text-slate-100">Live Opportunity Feed</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex items-center justify-center">
          <p className="text-sm text-slate-500">Loading opportunities...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-slate-800 bg-slate-950 h-full flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="h-4 w-4 text-amber-400" />
            <CardTitle className="text-base font-bold text-slate-50">
              Live Opportunity Feed
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
            <Badge className="bg-amber-500/10 text-amber-400 border-amber-500/20 text-[10px]">
              {opportunities.length} Active
            </Badge>
          </div>
        </div>
      </CardHeader>
      <ScrollArea className="flex-1 px-4 pb-4 overflow-y-auto">
        {error && opportunities.length === 0 && (
          <div className="rounded-lg border border-rose-800 bg-rose-950/20 p-4 mb-4">
            <p className="text-xs text-rose-300">Failed to load opportunities. Check browser console for details.</p>
          </div>
        )}
        <div className="space-y-3">
          {opportunities
            .sort((a, b) => b.confidence_score - a.confidence_score)
            .map((opp) => (
              <OpportunityCard key={opp.id} opp={opp} />
            ))}
        </div>
      </ScrollArea>
    </Card>
  );
}
