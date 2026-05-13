"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiOpportunity } from "@/lib/api";

export function useOpportunities(category?: string, minConfidence = 0) {
  const [opportunities, setOpportunities] = useState<ApiOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOpportunities = useCallback(async () => {
    try {
      setError(null);
      const data = await api.opportunities.list(category, minConfidence);
      setOpportunities(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch opportunities");
    } finally {
      setLoading(false);
    }
  }, [category, minConfidence]);

  useEffect(() => {
    fetchOpportunities();
    const interval = setInterval(fetchOpportunities, 30000);
    return () => clearInterval(interval);
  }, [fetchOpportunities]);

  return { opportunities, loading, error, refetch: fetchOpportunities };
}
