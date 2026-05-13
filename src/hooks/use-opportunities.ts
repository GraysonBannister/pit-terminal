"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiOpportunity } from "@/lib/api";
import { mockOpportunities } from "@/lib/mockApi";

export function useOpportunities(category?: string, minConfidence = 0) {
  const [opportunities, setOpportunities] = useState<ApiOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [usingMock, setUsingMock] = useState(false);

  const fetchOpportunities = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.opportunities.list(category, minConfidence);
      setOpportunities(data);
      setUsingMock(false);
    } catch {
      let filtered = category
        ? mockOpportunities.filter((o) => o.category === category)
        : [...mockOpportunities];
      if (minConfidence > 0) {
        filtered = filtered.filter((o) => o.confidence_score >= minConfidence);
      }
      setOpportunities(filtered.sort((a, b) => b.confidence_score - a.confidence_score));
      setUsingMock(true);
    } finally {
      setLoading(false);
    }
  }, [category, minConfidence]);

  useEffect(() => {
    fetchOpportunities();
    const interval = setInterval(fetchOpportunities, 30000);
    return () => clearInterval(interval);
  }, [fetchOpportunities]);

  return { opportunities, loading, usingMock, refetch: fetchOpportunities };
}
