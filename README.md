# PIT Terminal — Prediction Intelligence

Real-time probability intelligence infrastructure for prediction markets. Detects when market-implied probability materially diverges from reality-adjusted probability.

## Overview

PIT Terminal is an MVP built from the [Prediction Intelligence Terminal framework](overview.txt). It tracks prediction markets, aggregates information signals, and surfaces potentially mispriced opportunities.

**Core positioning:** Analytics and intelligence, not gambling.

## Features

- **Live Opportunity Feed** — Ranked mispricing opportunities with confidence scores, supporting signals, and divergence classification (undervalued / overvalued)
- **Narrative Shift Tracker** — Sentiment changes, attention spikes, narrative velocity, and source volume across tracked topics
- **Cross-Market Arbitrage** — Probability comparison across Polymarket, Kalshi, crypto markets, and more with disagreement scoring
- **Market Detail Pages** — Price history charts, AI summaries, sentiment analysis gauges, and relevant news aggregation
- **Dark Intelligence Terminal UI** — Professional analytics aesthetic optimized for monitoring

## Tech Stack

- **Frontend:** Next.js 16, React 19, TypeScript, Tailwind CSS, shadcn/ui
- **Charts:** Recharts
- **Icons:** Lucide React

## Data

The MVP uses realistic demo data covering:
- Politics (US election, Japan snap election, Ukraine ceasefire)
- Macro (Fed rate cuts, recession probability)
- Tech (OpenAI GPT-5, Apple Vision Pro)
- Crypto (Bitcoin $100K)

Each market includes price history, sentiment scores, AI summaries, and related news items.

## Running Locally

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Pages

| Route | Description |
|-------|-------------|
| `/` | Dashboard with opportunity feed, narrative tracker, cross-market table, and market list |
| `/opportunities` | Full-screen opportunity feed |
| `/narratives` | Full-screen narrative shift tracker |
| `/cross-market` | Cross-market arbitrage comparisons |
| `/markets` | All active markets |
| `/market/[id]` | Individual market detail with chart, AI summary, sentiment, and news |

## Notes

- This is an MVP with mock/demo data. Production would connect to live Polymarket/Kalshi APIs, news feeds, and an AI interpretation pipeline.
- The build currently works best in dev mode due to a known Next.js 16 + React 19 static generation compatibility issue. Use `npm run dev` for evaluation.
