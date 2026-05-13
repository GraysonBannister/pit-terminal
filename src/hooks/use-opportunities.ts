"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiOpportunity } from "@/lib/api";

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true";

export function useOpportunities(category?: string, minConfidence = 0) {
  const [opportunities, setOpportunities] = useState<ApiOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchOpportunities = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.opportunities.list(category, minConfidence);
      setOpportunities(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Failed to fetch opportunities"));
      if (USE_MOCK) {
        const { mockOpportunities } = await import("@/lib/mockApi");
        let filtered = category
          ? mockOpportunities.filter((o) => o.category === category)
          : [...mockOpportunities];
        if (minConfidence > 0) {
          filtered = filtered.filter((o) => o.confidence_score >= minConfidence);
        }
        setOpportunities(filtered.sort((a, b) => b.confidence_score - a.confidence_score));
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

  return { opportunities, loading, error, usingMock: USE_MOCK && !!error, refetch: fetchOpportunities };
}
