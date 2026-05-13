"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiMarket } from "@/lib/api";
import { mockMarkets } from "@/lib/mockApi";

const isLocalhost = typeof window !== "undefined" && window.location.hostname === "localhost";

export function useMarkets(category?: string) {
  const [markets, setMarkets] = useState<ApiMarket[]>([]);
  const [loading, setLoading] = useState(true);
  const [usingMock, setUsingMock] = useState(false);

  const fetchMarkets = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.markets.list(category);
      setMarkets(data);
      setUsingMock(false);
    } catch {
      // Fallback to mock data
      const filtered = category
        ? mockMarkets.filter((m) => m.category === category)
        : mockMarkets;
      setMarkets(filtered);
      setUsingMock(true);
    } finally {
      setLoading(false);
    }
  }, [category]);

  useEffect(() => {
    fetchMarkets();
    const interval = setInterval(fetchMarkets, 30000);
    return () => clearInterval(interval);
  }, [fetchMarkets]);

  return { markets, loading, usingMock, refetch: fetchMarkets };
}

export function useMarket(id: string) {
  const [market, setMarket] = useState<ApiMarket | null>(null);
  const [loading, setLoading] = useState(true);
  const [usingMock, setUsingMock] = useState(false);

  const fetchMarket = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.markets.get(id);
      setMarket(data);
      setUsingMock(false);
    } catch {
      const found = mockMarkets.find((m) => m.id === id) || null;
      setMarket(found);
      setUsingMock(true);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchMarket();
    const interval = setInterval(fetchMarket, 30000);
    return () => clearInterval(interval);
  }, [fetchMarket]);

  return { market, loading, usingMock, refetch: fetchMarket };
}
