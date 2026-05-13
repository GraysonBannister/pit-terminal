"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiCrossMarket } from "@/lib/api";

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true";

export function useCrossMarket() {
  const [comparisons, setComparisons] = useState<ApiCrossMarket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchComparisons = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.crossMarket.list();
      setComparisons(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Failed to fetch cross-market data"));
      if (USE_MOCK) {
        const { mockCrossMarket } = await import("@/lib/mockApi");
        setComparisons(mockCrossMarket);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchComparisons();
    const interval = setInterval(fetchComparisons, 30000);
    return () => clearInterval(interval);
  }, [fetchComparisons]);

  return { comparisons, loading, error, usingMock: USE_MOCK && !!error, refetch: fetchComparisons };
}
