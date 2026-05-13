"use client";

import { useNarratives } from "@/hooks/use-narratives";
import { getCategoryColor } from "@/lib/data";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { TrendingUp, TrendingDown, Activity, Clock } from "lucide-react";

export function NarrativeTracker() {
  const { narratives, loading, usingMock, error } = useNarratives();

  if (loading && narratives.length === 0) {
    return (
      <Card className="border-slate-800 bg-slate-950 h-full flex flex-col">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold text-slate-100">Narrative Shift Tracker</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex items-center justify-center">
          <p className="text-sm text-slate-500">Loading narratives...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-slate-800 bg-slate-950 h-full flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-indigo-400" />
            <CardTitle className="text-base font-bold text-slate-50">
              Narrative Shift Tracker
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
          </div>
        </div>
      </CardHeader>
      <ScrollArea className="flex-1 px-4 pb-4 overflow-y-auto">
        {error && narratives.length === 0 && (
          <div className="rounded-lg border border-rose-800 bg-rose-950/20 p-4 mb-4">
            <p className="text-xs text-rose-300">Failed to load narratives. Check browser console for details.</p>
          </div>
        )}
        <div className="space-y-3">
          {narratives
            .sort((a, b) => b.velocity - a.velocity)
            .map((nar) => {
              const delta = nar.current_sentiment - nar.previous_sentiment;
              return (
                <div
                  key={nar.id}
                  className="rounded-lg border border-slate-800 bg-slate-900/50 p-3 transition-colors hover:border-slate-700"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge
                          variant="outline"
                          className={`text-xs uppercase tracking-wide ${getCategoryColor(nar.category)}`}
                        >
                          {nar.category}
                        </Badge>
                        <span className="flex items-center gap-1.5 text-sm text-slate-400">
                          <Clock className="h-4 w-4" />
                          {new Date(nar.last_updated).toLocaleTimeString()}
                        </span>
                      </div>
                      <p className="text-base font-medium text-slate-100 truncate leading-snug">
                        {nar.topic}
                      </p>
                    </div>
                    <div className="flex items-center gap-1.5 rounded-md bg-slate-950 px-3 py-1.5">
                      {delta >= 0 ? (
                        <TrendingUp className="h-4 w-4 text-emerald-400" />
                      ) : (
                        <TrendingDown className="h-4 w-4 text-rose-400" />
                      )}
                      <span
                        className={`text-sm font-bold ${
                          delta >= 0 ? "text-emerald-400" : "text-rose-400"
                        }`}
                      >
                        {delta >= 0 ? "+" : ""}
                        {(delta * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <div className="mt-4 grid grid-cols-3 gap-3">
                    <div className="rounded-lg bg-slate-950 px-3 py-2">
                      <p className="text-xs font-medium text-slate-500 mb-1">Velocity</p>
                      <p className="text-sm font-bold text-slate-200">
                        {(nar.velocity * 100).toFixed(0)}%
                      </p>
                    </div>
                    <div className="rounded-lg bg-slate-950 px-3 py-2">
                      <p className="text-xs font-medium text-slate-500 mb-1">Attention</p>
                      <p className="text-sm font-bold text-slate-200">
                        {nar.attention_spike.toFixed(1)}x
                      </p>
                    </div>
                    <div className="rounded-lg bg-slate-950 px-3 py-2">
                      <p className="text-xs font-medium text-slate-500 mb-1">Sources</p>
                      <p className="text-sm font-bold text-slate-200">
                        {nar.sources}
                      </p>
                    </div>
                  </div>

                  <div className="mt-3">
                    <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-indigo-500 transition-all"
                        style={{ width: `${nar.current_sentiment * 100}%` }}
                      />
                    </div>
                    <div className="mt-2 flex justify-between text-sm text-slate-400">
                      <span className="font-medium">Sentiment: <span className="text-slate-200">{(nar.current_sentiment * 100).toFixed(0)}%</span></span>
                      <span className="font-medium">from <span className="text-slate-200">{(nar.previous_sentiment * 100).toFixed(0)}%</span></span>
                    </div>
                  </div>
                </div>
              );
            })}
        </div>
      </ScrollArea>
    </Card>
  );
}
