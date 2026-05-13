import { Market, Opportunity, NarrativeShift, CrossMarketComparison, NewsItem } from "./types";

function generatePriceHistory(baseProb: number, days = 14): Market["priceHistory"] {
  const history: Market["priceHistory"] = [];
  let prob = baseProb;
  const now = new Date();
  for (let i = days * 4; i >= 0; i--) {
    const change = (Math.random() - 0.48) * 0.04;
    prob = Math.max(0.02, Math.min(0.98, prob + change));
    history.push({
      timestamp: new Date(now.getTime() - i * 6 * 60 * 60 * 1000).toISOString(),
      probability: prob,
      volume: Math.floor(Math.random() * 500000) + 10000,
    });
  }
  return history;
}

export const markets: Market[] = [
  {
    id: "pol-001",
    title: "Trump wins 2024 US Presidential Election",
    category: "politics",
    probability: 0.52,
    volume: 14200000,
    liquidity: 2800000,
    spread: 0.01,
    recentMovement: -0.03,
    resolutionDate: "2024-11-05",
    source: "Polymarket",
    priceHistory: generatePriceHistory(0.52),
    aiSummary:
      "Recent polling data from swing states shows tightening race. Post-debate sentiment shifted slightly negative. Economic indicators remain favorable to incumbent positioning.",
    sentiment: {
      confidence: 0.64,
      uncertainty: 0.28,
      polarization: 0.82,
      narrativeVelocity: 0.45,
    },
    tags: ["usa", "election", "trump", "biden", "presidency"],
  },
  {
    id: "pol-002",
    title: "Japan PM announces snap election before Oct 2024",
    category: "politics",
    probability: 0.34,
    volume: 890000,
    liquidity: 210000,
    spread: 0.04,
    recentMovement: 0.12,
    resolutionDate: "2024-10-01",
    source: "Polymarket",
    priceHistory: generatePriceHistory(0.34),
    aiSummary:
      "Internal LDP dissent rising. Opposition coordination improving. Media speculation intensifying following approval rating drop below 30%. Historical precedent suggests elevated risk.",
    sentiment: {
      confidence: 0.41,
      uncertainty: 0.51,
      polarization: 0.55,
      narrativeVelocity: 0.78,
    },
    tags: ["japan", "election", "ldp", "snap-election", "asia"],
  },
  {
    id: "pol-003",
    title: "Ukraine-Russia ceasefire by end of 2024",
    category: "politics",
    probability: 0.18,
    volume: 3200000,
    liquidity: 540000,
    spread: 0.02,
    recentMovement: -0.05,
    resolutionDate: "2024-12-31",
    source: "Polymarket",
    priceHistory: generatePriceHistory(0.18),
    aiSummary:
      "Diplomatic channels remain frozen. Battlefield stalemate continues. Western fatigue narrative growing but no concrete policy shift detected. Energy price pressures easing, reducing urgency.",
    sentiment: {
      confidence: 0.38,
      uncertainty: 0.44,
      polarization: 0.67,
      narrativeVelocity: 0.22,
    },
    tags: ["ukraine", "russia", "war", "ceasefire", "diplomacy"],
  },
  {
    id: "mac-001",
    title: "Fed cuts rates in September 2024",
    category: "macro",
    probability: 0.76,
    volume: 9500000,
    liquidity: 1900000,
    spread: 0.01,
    recentMovement: 0.08,
    resolutionDate: "2024-09-18",
    source: "Kalshi",
    priceHistory: generatePriceHistory(0.76),
    aiSummary:
      "CPI prints trending lower. Labor market showing signs of cooling. Fed officials increasingly dovish in speeches. Market pricing 100bps of cuts by year-end.",
    sentiment: {
      confidence: 0.72,
      uncertainty: 0.19,
      polarization: 0.31,
      narrativeVelocity: 0.55,
    },
    tags: ["fed", "rates", "cpi", "inflation", "usa"],
  },
  {
    id: "mac-002",
    title: "US enters recession in Q3 2024",
    category: "macro",
    probability: 0.29,
    volume: 4100000,
    liquidity: 780000,
    spread: 0.03,
    recentMovement: -0.04,
    resolutionDate: "2024-09-30",
    source: "Kalshi",
    priceHistory: generatePriceHistory(0.29),
    aiSummary:
      "Leading indicators mixed. ISM manufacturing below 50 but services resilient. Yield curve un-inverting historically precedes recession by 6-18 months.",
    sentiment: {
      confidence: 0.51,
      uncertainty: 0.39,
      polarization: 0.48,
      narrativeVelocity: 0.33,
    },
    tags: ["recession", "usa", "gdp", "economy"],
  },
  {
    id: "tec-001",
    title: "OpenAI releases GPT-5 before end of 2024",
    category: "tech",
    probability: 0.22,
    volume: 1800000,
    liquidity: 340000,
    spread: 0.05,
    recentMovement: -0.08,
    resolutionDate: "2024-12-31",
    source: "Polymarket",
    priceHistory: generatePriceHistory(0.22),
    aiSummary:
      "Altman repeatedly stated no GPT-5 this year. o1 reasoning model just released. Organizational focus on safety and alignment. Competition from Anthropic and Google intensifying.",
    sentiment: {
      confidence: 0.58,
      uncertainty: 0.31,
      polarization: 0.42,
      narrativeVelocity: 0.61,
    },
    tags: ["openai", "gpt", "ai", "llm", "tech"],
  },
  {
    id: "tec-002",
    title: "Apple Vision Pro sales exceed 1M units in 2024",
    category: "tech",
    probability: 0.44,
    volume: 670000,
    liquidity: 140000,
    spread: 0.06,
    recentMovement: 0.03,
    resolutionDate: "2024-12-31",
    source: "Polymarket",
    priceHistory: generatePriceHistory(0.44),
    aiSummary:
      "Early sales strong but reviews mixed on utility. Price point limiting mass adoption. Enterprise traction emerging. Supply chain rumors suggest cheaper model in development.",
    sentiment: {
      confidence: 0.49,
      uncertainty: 0.37,
      polarization: 0.39,
      narrativeVelocity: 0.28,
    },
    tags: ["apple", "vision-pro", "vr", "hardware"],
  },
  {
    id: "cry-001",
    title: "Bitcoin hits $100K before end of 2024",
    category: "crypto",
    probability: 0.31,
    volume: 12000000,
    liquidity: 2400000,
    spread: 0.02,
    recentMovement: 0.15,
    resolutionDate: "2024-12-31",
    source: "Crypto",
    priceHistory: generatePriceHistory(0.31),
    aiSummary:
      "ETF inflows sustaining price floor. Halving supply dynamics playing out. Institutional adoption accelerating. Regulatory clarity improving in US and Asia.",
    sentiment: {
      confidence: 0.55,
      uncertainty: 0.35,
      polarization: 0.71,
      narrativeVelocity: 0.67,
    },
    tags: ["bitcoin", "crypto", "btc", "etf"],
  },
];

export const opportunities: Opportunity[] = [
  {
    id: "opp-001",
    marketId: "pol-002",
    marketTitle: "Japan PM announces snap election before Oct 2024",
    category: "politics",
    marketProbability: 0.34,
    aiEstimatedRange: [0.48, 0.62],
    confidenceScore: 78,
    divergenceType: "undervalued",
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    signals: [
      {
        type: "news",
        label: "Credibility Shift",
        description: "Nikkei reports LDP faction leaders met privately to discuss timeline",
        strength: 0.82,
        source: "Nikkei",
      },
      {
        type: "sentiment",
        label: "Narrative Velocity Spike",
        description: "Japanese political discourse sentiment shifting 3x faster than baseline",
        strength: 0.76,
      },
      {
        type: "liquidity",
        label: "Thin Liquidity",
        description: "Low liquidity may be suppressing price discovery",
        strength: 0.54,
      },
    ],
  },
  {
    id: "opp-002",
    marketId: "mac-001",
    marketTitle: "Fed cuts rates in September 2024",
    category: "macro",
    marketProbability: 0.76,
    aiEstimatedRange: [0.55, 0.68],
    confidenceScore: 64,
    divergenceType: "overvalued",
    createdAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
    signals: [
      {
        type: "news",
        label: "Contradictory Signal",
        description: "Core PCE reaccelerated slightly; market may be overpricing cuts",
        strength: 0.68,
        source: "Bloomberg",
      },
      {
        type: "cross_market",
        label: "SOFR Disagreement",
        description: "SOFR futures implying 65bps vs market pricing 100bps",
        strength: 0.71,
      },
    ],
  },
  {
    id: "opp-003",
    marketId: "tec-001",
    marketTitle: "OpenAI releases GPT-5 before end of 2024",
    category: "tech",
    marketProbability: 0.22,
    aiEstimatedRange: [0.08, 0.15],
    confidenceScore: 71,
    divergenceType: "overvalued",
    createdAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
    signals: [
      {
        type: "news",
        label: "Direct Statement",
        description: "Altman explicitly ruled out GPT-5 in 2024 at recent conference",
        strength: 0.91,
        source: "The Verge",
      },
      {
        type: "narrative",
        label: "Hype Decay",
        description: "Social volume on GPT-5 declining despite new model releases",
        strength: 0.63,
      },
    ],
  },
  {
    id: "opp-004",
    marketId: "cry-001",
    marketTitle: "Bitcoin hits $100K before end of 2024",
    category: "crypto",
    marketProbability: 0.31,
    aiEstimatedRange: [0.38, 0.52],
    confidenceScore: 58,
    divergenceType: "undervalued",
    createdAt: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
    signals: [
      {
        type: "cross_market",
        label: "Options Skew",
        description: "Deribit 100K calls pricing higher probability than spot markets",
        strength: 0.74,
      },
      {
        type: "sentiment",
        label: "Institutional Inflows",
        description: "ETF weekly inflows at record highs; narrative velocity positive",
        strength: 0.69,
      },
    ],
  },
];

export const narrativeShifts: NarrativeShift[] = [
  {
    id: "nar-001",
    topic: "Japan Snap Election",
    category: "politics",
    previousSentiment: 0.28,
    currentSentiment: 0.54,
    velocity: 0.82,
    attentionSpike: 3.4,
    sources: 14,
    lastUpdated: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    marketsAffected: ["pol-002"],
  },
  {
    id: "nar-002",
    topic: "Fed Rate Cut Consensus",
    category: "macro",
    previousSentiment: 0.62,
    currentSentiment: 0.71,
    velocity: 0.45,
    attentionSpike: 1.2,
    sources: 38,
    lastUpdated: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
    marketsAffected: ["mac-001"],
  },
  {
    id: "nar-003",
    topic: "Ukraine War Fatigue",
    category: "politics",
    previousSentiment: 0.41,
    currentSentiment: 0.33,
    velocity: 0.38,
    attentionSpike: 0.9,
    sources: 22,
    lastUpdated: new Date(Date.now() - 90 * 60 * 1000).toISOString(),
    marketsAffected: ["pol-003"],
  },
  {
    id: "nar-004",
    topic: "AI Model Release Cycle",
    category: "tech",
    previousSentiment: 0.58,
    currentSentiment: 0.44,
    velocity: 0.67,
    attentionSpike: 2.1,
    sources: 19,
    lastUpdated: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
    marketsAffected: ["tec-001"],
  },
  {
    id: "nar-005",
    topic: "Bitcoin Institutional Adoption",
    category: "crypto",
    previousSentiment: 0.48,
    currentSentiment: 0.63,
    velocity: 0.71,
    attentionSpike: 2.8,
    sources: 27,
    lastUpdated: new Date(Date.now() - 20 * 60 * 1000).toISOString(),
    marketsAffected: ["cry-001"],
  },
];

export const crossMarketComparisons: CrossMarketComparison[] = [
  {
    eventTitle: "Trump wins 2024 US Presidential Election",
    markets: [
      { source: "Polymarket", probability: 0.52, volume: 14200000, updatedAt: new Date(Date.now() - 5 * 60 * 1000).toISOString() },
      { source: "Kalshi", probability: 0.49, volume: 3200000, updatedAt: new Date(Date.now() - 12 * 60 * 1000).toISOString() },
      { source: "PredictIt", probability: 0.55, volume: 890000, updatedAt: new Date(Date.now() - 20 * 60 * 1000).toISOString() },
    ],
    disagreementScore: 0.12,
    arbitrageHint: "Polymarket/Kalshi spread widest in 48h",
  },
  {
    eventTitle: "Fed cuts rates in September 2024",
    markets: [
      { source: "Kalshi", probability: 0.76, volume: 9500000, updatedAt: new Date(Date.now() - 8 * 60 * 1000).toISOString() },
      { source: "CME FedWatch", probability: 0.65, volume: 0, updatedAt: new Date(Date.now() - 60 * 60 * 1000).toISOString() },
    ],
    disagreementScore: 0.16,
    arbitrageHint: "Kalshi pricing 11pts higher than CME implied odds",
  },
  {
    eventTitle: "Bitcoin hits $100K before end of 2024",
    markets: [
      { source: "Polymarket", probability: 0.31, volume: 12000000, updatedAt: new Date(Date.now() - 3 * 60 * 1000).toISOString() },
      { source: "Crypto Options", probability: 0.42, volume: 4500000, updatedAt: new Date(Date.now() - 15 * 60 * 1000).toISOString() },
    ],
    disagreementScore: 0.22,
    arbitrageHint: "Options market implying significantly higher probability",
  },
];

export const newsItems: NewsItem[] = [
  {
    id: "news-001",
    headline: "Japan LDP faction leaders hold emergency meeting on election timing",
    source: "Nikkei",
    credibility: 0.92,
    publishedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    tags: ["japan", "politics", "election"],
    summary: "Senior LDP members reportedly discussed snap election scenarios as approval ratings drop below 30%.",
    marketImpact: "Elevates probability of snap election call",
  },
  {
    id: "news-002",
    headline: "US Core PCE rises 0.2% month-over-month, slightly above expectations",
    source: "Bloomberg",
    credibility: 0.94,
    publishedAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
    tags: ["usa", "macro", "inflation", "fed"],
    summary: "The Fed's preferred inflation gauge showed sticky price pressures, complicating the case for aggressive rate cuts.",
    marketImpact: "May reduce likelihood of 50bps September cut",
  },
  {
    id: "news-003",
    headline: "OpenAI unveils o1 reasoning model, says GPT-5 not on 2024 roadmap",
    source: "The Verge",
    credibility: 0.88,
    publishedAt: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
    tags: ["tech", "openai", "ai"],
    summary: "CEO Sam Altman emphasized focus on reasoning capabilities over model scale in near term.",
    marketImpact: "Strong signal against GPT-5 in 2024",
  },
  {
    id: "news-004",
    headline: "Bitcoin ETF weekly inflows hit $1.2B, largest since launch",
    source: "Reuters",
    credibility: 0.91,
    publishedAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
    tags: ["crypto", "bitcoin", "etf"],
    summary: "Institutional demand for spot Bitcoin ETFs surged as macro outlook softened and regulatory clarity improved.",
    marketImpact: "Supports bullish Bitcoin price trajectory",
  },
  {
    id: "news-005",
    headline: "Ukraine-Russia prisoner exchange falls through after ceasefire talks stall",
    source: "AP",
    credibility: 0.93,
    publishedAt: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
    tags: ["ukraine", "russia", "war"],
    summary: "Diplomatic channels remain strained with both sides hardening positions ahead of winter.",
    marketImpact: "Reduces near-term ceasefire probability",
  },
];

export function getMarketById(id: string): Market | undefined {
  return markets.find((m) => m.id === id);
}

export function formatProbability(p: number): string {
  return `${(p * 100).toFixed(1)}%`;
}

export function formatVolume(v: number): string {
  if (v >= 1_000_000) return `$${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `$${(v / 1_000).toFixed(0)}K`;
  return `$${v}`;
}

export function formatTimeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export function getCategoryColor(category: string): string {
  switch (category) {
    case "politics":
      return "bg-blue-500/10 text-blue-400 border-blue-500/20";
    case "macro":
      return "bg-amber-500/10 text-amber-400 border-amber-500/20";
    case "tech":
      return "bg-purple-500/10 text-purple-400 border-purple-500/20";
    case "crypto":
      return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
    default:
      return "bg-slate-500/10 text-slate-400 border-slate-500/20";
  }
}
