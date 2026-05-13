"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiMarket } from "@/lib/api";

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true";

export function useMarkets(category?: string) {
  const [markets, setMarkets] = useState<ApiMarket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [usingMock, setUsingMock] = useState(false);

  const fetchMarkets = useCallback(async () => {
    console.log(`[useMarkets] Fetching markets (category=${category || "all"})...`);
    try {
      setLoading(true);
      setError(null);
      setUsingMock(false);
      const data = await api.markets.list(category);
      console.log(`[useMarkets] Got ${data.length} markets from API. First:`, data[0]?.title || "none");
      setMarkets(data);
    } catch (err) {
      console.error("[useMarkets] API fetch failed:", err);
      setError(err instanceof Error ? err : new Error("Failed to fetch markets"));
      if (USE_MOCK) {
        console.warn("[useMarkets] USE_MOCK=true, falling back to mock data");
        const { mockMarkets } = await import("@/lib/mockApi");
        const filtered = category
          ? mockMarkets.filter((m) => m.category === category)
          : mockMarkets;
        console.log(`[useMarkets] Loaded ${filtered.length} mock markets`);
        setMarkets(filtered);
        setUsingMock(true);
      } else {
        console.warn("[useMarkets] USE_MOCK=false, not loading mock data. Array will be empty.");
        setMarkets([]);
        setUsingMock(false);
      }
    } finally {
      setLoading(false);
    }
  }, [category]);

  useEffect(() => {
    fetchMarkets();
    const interval = setInterval(fetchMarkets, 30000);
    return () => clearInterval(interval);
  }, [fetchMarkets]);

  return { markets, loading, error, usingMock, refetch: fetchMarkets };
}

export function useMarket(id: string) {
  const [market, setMarket] = useState<ApiMarket | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [usingMock, setUsingMock] = useState(false);

  const fetchMarket = useCallback(async () => {
    console.log(`[useMarket] Fetching market id=${id}...`);
    try {
      setLoading(true);
      setError(null);
      setUsingMock(false);
      const data = await api.markets.get(id);
      console.log(`[useMarket] Got market from API:`, data.title);
      setMarket(data);
    } catch (err) {
      console.error("[useMarket] API fetch failed:", err);
      setError(err instanceof Error ? err : new Error("Failed to fetch market"));
      if (USE_MOCK) {
        console.warn("[useMarket] USE_MOCK=true, falling back to mock data");
        const { mockMarkets } = await import("@/lib/mockApi");
        const found = mockMarkets.find((m) => m.id === id) || null;
        setMarket(found);
        setUsingMock(true);
      } else {
        setMarket(null);
        setUsingMock(false);
      }
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchMarket();
    const interval = setInterval(fetchMarket, 30000);
    return () => clearInterval(interval);
  }, [fetchMarket]);

  return { market, loading, error, usingMock, refetch: fetchMarket };
}
