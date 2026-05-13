export interface Market {
  id: string;
  title: string;
  category: "politics" | "macro" | "tech" | "crypto";
  probability: number;
  volume: number;
  liquidity: number;
  spread: number;
  recentMovement: number;
  resolutionDate: string;
  source: "Polymarket" | "Kalshi" | "Crypto";
  priceHistory: PricePoint[];
  aiSummary?: string;
  sentiment: SentimentScore;
  tags: string[];
}

export interface PricePoint {
  timestamp: string;
  probability: number;
  volume: number;
}

export interface SentimentScore {
  confidence: number;
  uncertainty: number;
  polarization: number;
  narrativeVelocity: number;
}

export interface Opportunity {
  id: string;
  marketId: string;
  marketTitle: string;
  category: string;
  marketProbability: number;
  aiEstimatedRange: [number, number];
  confidenceScore: number;
  signals: Signal[];
  createdAt: string;
  divergenceType: "undervalued" | "overvalued" | "disagreement";
}

export interface Signal {
  type: "news" | "sentiment" | "cross_market" | "liquidity" | "narrative";
  label: string;
  description: string;
  strength: number;
  source?: string;
}

export interface NarrativeShift {
  id: string;
  topic: string;
  category: string;
  previousSentiment: number;
  currentSentiment: number;
  velocity: number;
  attentionSpike: number;
  sources: number;
  lastUpdated: string;
  marketsAffected: string[];
}

export interface CrossMarketComparison {
  eventTitle: string;
  markets: {
    source: string;
    probability: number;
    volume: number;
    updatedAt: string;
  }[];
  disagreementScore: number;
  arbitrageHint?: string;
}

export interface NewsItem {
  id: string;
  headline: string;
  source: string;
  credibility: number;
  publishedAt: string;
  tags: string[];
  summary: string;
  marketImpact?: string;
}
