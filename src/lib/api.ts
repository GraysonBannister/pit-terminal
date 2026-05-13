const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text().catch(() => "Unknown error");
    throw new Error(`API ${res.status}: ${err}`);
  }
  return res.json() as Promise<T>;
}

export interface ApiMarket {
  id: string;
  title: string;
  category: string;
  probability: number;
  volume: number;
  liquidity: number;
  spread: number;
  recent_movement: number;
  resolution_date: string;
  source: string;
  ai_summary: string | null;
  sentiment: {
    confidence: number;
    uncertainty: number;
    polarization: number;
    narrative_velocity: number;
  } | null;
  tags: string[];
  created_at: string;
  updated_at: string;
  price_history?: {
    timestamp: string;
    probability: number;
    volume: number;
  }[];
}

export interface ApiOpportunity {
  id: string;
  market_id: string;
  market_title: string;
  category: string;
  market_probability: number;
  ai_estimated_low: number;
  ai_estimated_high: number;
  confidence_score: number;
  divergence_type: "undervalued" | "overvalued" | "disagreement";
  signals: {
    type: string;
    label: string;
    description: string;
    strength: number;
    source?: string;
  }[];
  created_at: string;
}

export interface ApiNarrative {
  id: string;
  topic: string;
  category: string;
  previous_sentiment: number;
  current_sentiment: number;
  velocity: number;
  attention_spike: number;
  sources: number;
  last_updated: string;
  markets_affected: string[];
  created_at: string;
}

export interface ApiNewsItem {
  id: string;
  headline: string;
  source: string;
  credibility: number;
  published_at: string;
  tags: string[];
  summary: string;
  market_impact: string | null;
}

export const api = {
  markets: {
    list: (category?: string, limit = 50) =>
      fetchJson<ApiMarket[]>(`/markets?${category ? `category=${category}&` : ""}limit=${limit}`),
    get: (id: string) => fetchJson<ApiMarket>(`/markets/${id}`),
  },
  opportunities: {
    list: (category?: string, minConfidence = 0, limit = 20) =>
      fetchJson<ApiOpportunity[]>(
        `/opportunities?${category ? `category=${category}&` : ""}${minConfidence > 0 ? `min_confidence=${minConfidence}&` : ""}limit=${limit}`
      ),
  },
  narratives: {
    list: (category?: string, limit = 20) =>
      fetchJson<ApiNarrative[]>(`/narratives?${category ? `category=${category}&` : ""}limit=${limit}`),
  },
  news: {
    list: (tag?: string, limit = 20) =>
      fetchJson<ApiNewsItem[]>(`/news?${tag ? `tag=${tag}&` : ""}limit=${limit}`),
  },
};
