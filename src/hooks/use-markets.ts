"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiMarket } from "@/lib/api";

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true";

export function useMarkets(category?: string) {
  const [markets, setMarkets] = useState<ApiMarket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchMarkets = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.markets.list(category);
      setMarkets(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Failed to fetch markets"));
      if (USE_MOCK) {
        const { mockMarkets } = await import("@/lib/mockApi");
        const filtered = category
          ? mockMarkets.filter((m) => m.category === category)
          : mockMarkets;
        setMarkets(filtered);
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

  return { markets, loading, error, usingMock: USE_MOCK && !!error, refetch: fetchMarkets };
}

export function useMarket(id: string) {
  const [market, setMarket] = useState<ApiMarket | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchMarket = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.markets.get(id);
      setMarket(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Failed to fetch market"));
      if (USE_MOCK) {
        const { mockMarkets } = await import("@/lib/mockApi");
        const found = mockMarkets.find((m) => m.id === id) || null;
        setMarket(found);
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

  return { market, loading, error, usingMock: USE_MOCK && !!error, refetch: fetchMarket };
}
