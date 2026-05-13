"use client";

import React from "react";
import { useMarket } from "@/hooks/use-markets";
import { useNews } from "@/hooks/use-news";
import { formatProbability, formatVolume, getCategoryColor } from "@/lib/data";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PriceChart } from "@/components/price-chart";
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Minus,
  Brain,
  Newspaper,
  Activity,
  Droplets,
  Calendar,
  Tag,
  BarChart3,
} from "lucide-react";
import Link from "next/link";

export default function MarketDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = React.use(params);
  const { market, loading } = useMarket(id);
  const { news: allNews } = useNews();

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <p className="text-slate-500">Loading market data...</p>
      </div>
    );
  }

  if (!market) {
    return (
      <div className="flex h-96 items-center justify-center">
        <p className="text-rose-400">Market not found</p>
      </div>
    );
  }

  const relatedNews = allNews.filter((n) =>
    (market.tags || []).some((t: string) => n.tags.includes(t))
  );

  const sentiment = market.sentiment || {
    confidence: 0.5,
    uncertainty: 0.5,
    polarization: 0.5,
    narrative_velocity: 0.5,
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link
          href="/"
          className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </Link>
      </div>

      <div className="flex items-start justify-between gap-6">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <Badge
              variant="outline"
              className={`text-[10px] uppercase ${getCategoryColor(market.category)}`}
            >
              {market.category}
            </Badge>
            <span className="text-xs text-slate-500">{market.source}</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100">{market.title}</h1>
          <div className="mt-3 flex flex-wrap gap-2">
            {(market.tags || []).map((tag: string) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 rounded-full border border-slate-800 bg-slate-900 px-2 py-0.5 text-[10px] text-slate-400"
              >
                <Tag className="h-3 w-3" />
                {tag}
              </span>
            ))}
          </div>
        </div>
        <div className="flex flex-col items-end gap-2">
          <span className="text-3xl font-bold text-slate-100">
            {formatProbability(market.probability)}
          </span>
          <div className="flex items-center gap-1">
            {market.recent_movement > 0 ? (
              <TrendingUp className="h-4 w-4 text-emerald-400" />
            ) : market.recent_movement < 0 ? (
              <TrendingDown className="h-4 w-4 text-rose-400" />
            ) : (
              <Minus className="h-4 w-4 text-slate-500" />
            )}
            <span
              className={`text-sm font-medium ${
                market.recent_movement > 0
                  ? "text-emerald-400"
                  : market.recent_movement < 0
                  ? "text-rose-400"
                  : "text-slate-500"
              }`}
            >
              {market.recent_movement > 0 ? "+" : ""}
              {(market.recent_movement * 100).toFixed(1)}% today
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3">
        <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-3">
          <div className="flex items-center gap-2 text-[10px] uppercase tracking-wider text-slate-500">
            <BarChart3 className="h-3 w-3" />
            Volume
          </div>
          <p className="mt-1 text-lg font-bold text-slate-200">
            {formatVolume(market.volume)}
          </p>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-3">
          <div className="flex items-center gap-2 text-[10px] uppercase tracking-wider text-slate-500">
            <Droplets className="h-3 w-3" />
            Liquidity
          </div>
          <p className="mt-1 text-lg font-bold text-slate-200">
            {formatVolume(market.liquidity)}
          </p>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-3">
          <div className="flex items-center gap-2 text-[10px] uppercase tracking-wider text-slate-500">
            <Activity className="h-3 w-3" />
            Spread
          </div>
          <p className="mt-1 text-lg font-bold text-slate-200">
            {(market.spread * 100).toFixed(1)}%
          </p>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-3">
          <div className="flex items-center gap-2 text-[10px] uppercase tracking-wider text-slate-500">
            <Calendar className="h-3 w-3" />
            Resolves
          </div>
          <p className="mt-1 text-lg font-bold text-slate-200">
            {market.resolution_date || "TBD"}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 border-slate-800 bg-slate-950">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold text-slate-100">
              Probability History
            </CardTitle>
          </CardHeader>
          <CardContent>
            <PriceChart
              data={
                market.price_history?.map((p) => ({
                  timestamp: p.timestamp,
                  probability: p.probability,
                  volume: p.volume,
                })) || []
              }
            />
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card className="border-slate-800 bg-slate-950">
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <Brain className="h-4 w-4 text-indigo-400" />
                <CardTitle className="text-sm font-semibold text-slate-100">
                  AI Summary
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed text-slate-300">
                {market.ai_summary || "No AI summary available yet."}
              </p>
            </CardContent>
          </Card>

          <Card className="border-slate-800 bg-slate-950">
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-purple-400" />
                <CardTitle className="text-sm font-semibold text-slate-100">
                  Sentiment Analysis
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                { label: "Confidence", value: sentiment.confidence },
                { label: "Uncertainty", value: sentiment.uncertainty },
                { label: "Polarization", value: sentiment.polarization },
                { label: "Narrative Velocity", value: sentiment.narrative_velocity },
              ].map((s) => (
                <div key={s.label}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-slate-400">{s.label}</span>
                    <span className="text-xs font-medium text-slate-200">
                      {(s.value * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-indigo-500 transition-all"
                      style={{ width: `${s.value * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>

      <Card className="border-slate-800 bg-slate-950">
        <CardHeader className="pb-2">
          <div className="flex items-center gap-2">
            <Newspaper className="h-4 w-4 text-slate-400" />
            <CardTitle className="text-sm font-semibold text-slate-100">
              Relevant News
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          {relatedNews.length === 0 ? (
            <p className="text-sm text-slate-500">No directly related news items.</p>
          ) : (
            <div className="space-y-3">
              {relatedNews.map((news) => (
                <div
                  key={news.id}
                  className="rounded-lg border border-slate-800 bg-slate-900/50 p-4"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-medium text-indigo-400">
                      {news.source}
                    </span>
                    <span className="text-[10px] text-slate-500">
                      Credibility {(news.credibility * 100).toFixed(0)}%
                    </span>
                    <span className="text-[10px] text-slate-500">
                      {new Date(news.published_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm font-medium text-slate-200">
                    {news.headline}
                  </p>
                  <p className="mt-1 text-xs text-slate-400">{news.summary}</p>
                  {news.market_impact && (
                    <div className="mt-2 inline-flex items-center gap-1.5 rounded-md bg-indigo-500/10 px-2 py-1 text-[10px] text-indigo-300">
                      <Brain className="h-3 w-3" />
                      {news.market_impact}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
