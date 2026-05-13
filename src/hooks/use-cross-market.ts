"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiCrossMarket } from "@/lib/api";

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true";

export function useCrossMarket() {
  const [comparisons, setComparisons] = useState<ApiCrossMarket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [usingMock, setUsingMock] = useState(false);

  const fetchComparisons = useCallback(async () => {
    console.log("[useCrossMarket] Fetching cross-market comparisons...");
    try {
      setLoading(true);
      setError(null);
      setUsingMock(false);
      const data = await api.crossMarket.list();
      console.log(`[useCrossMarket] Got ${data.length} comparisons from API. First:`, data[0]?.event_title || "none");
      setComparisons(data);
    } catch (err) {
      console.error("[useCrossMarket] API fetch failed:", err);
      setError(err instanceof Error ? err : new Error("Failed to fetch cross-market data"));
      if (USE_MOCK) {
        console.warn("[useCrossMarket] USE_MOCK=true, falling back to mock data");
        const { mockCrossMarket } = await import("@/lib/mockApi");
        console.log(`[useCrossMarket] Loaded ${mockCrossMarket.length} mock comparisons`);
        setComparisons(mockCrossMarket);
        setUsingMock(true);
      } else {
        console.warn("[useCrossMarket] USE_MOCK=false, not loading mock data. Array will be empty.");
        setComparisons([]);
        setUsingMock(false);
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

  return { comparisons, loading, error, usingMock, refetch: fetchComparisons };
}
