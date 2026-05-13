"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiOpportunity } from "@/lib/api";

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true";

export function useOpportunities(category?: string, minConfidence = 0) {
  const [opportunities, setOpportunities] = useState<ApiOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [usingMock, setUsingMock] = useState(false);

  const fetchOpportunities = useCallback(async () => {
    console.log(`[useOpportunities] Fetching opportunities (category=${category || "all"}, minConfidence=${minConfidence})...`);
    try {
      setLoading(true);
      setError(null);
      setUsingMock(false);
      const data = await api.opportunities.list(category, minConfidence);
      console.log(`[useOpportunities] Got ${data.length} opportunities from API. First:`, data[0]?.market_title || "none");
      setOpportunities(data);
    } catch (err) {
      console.error("[useOpportunities] API fetch failed:", err);
      setError(err instanceof Error ? err : new Error("Failed to fetch opportunities"));
      if (USE_MOCK) {
        console.warn("[useOpportunities] USE_MOCK=true, falling back to mock data");
        const { mockOpportunities } = await import("@/lib/mockApi");
        let filtered = category
          ? mockOpportunities.filter((o) => o.category === category)
          : [...mockOpportunities];
        if (minConfidence > 0) {
          filtered = filtered.filter((o) => o.confidence_score >= minConfidence);
        }
        console.log(`[useOpportunities] Loaded ${filtered.length} mock opportunities`);
        setOpportunities(filtered.sort((a, b) => b.confidence_score - a.confidence_score));
        setUsingMock(true);
      } else {
        console.warn("[useOpportunities] USE_MOCK=false, not loading mock data. Array will be empty.");
        setOpportunities([]);
        setUsingMock(false);
      }
    } finally {
      setLoading(false);
    }
  }, [category, minConfidence]);

  useEffect(() => {
    fetchOpportunities();
    const interval = setInterval(fetchOpportunities, 30000);
    return () => clearInterval(interval);
  }, [fetchOpportunities]);

  return { opportunities, loading, error, usingMock, refetch: fetchOpportunities };
}
