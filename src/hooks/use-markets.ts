"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiMarket } from "@/lib/api";

export function useMarkets(category?: string) {
  const [markets, setMarkets] = useState<ApiMarket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMarkets = useCallback(async () => {
    try {
      setError(null);
      const data = await api.markets.list(category);
      setMarkets(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch markets");
    } finally {
      setLoading(false);
    }
  }, [category]);

  useEffect(() => {
    fetchMarkets();
    const interval = setInterval(fetchMarkets, 30000);
    return () => clearInterval(interval);
  }, [fetchMarkets]);

  return { markets, loading, error, refetch: fetchMarkets };
}

export function useMarket(id: string) {
  const [market, setMarket] = useState<ApiMarket | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMarket = useCallback(async () => {
    try {
      setError(null);
      const data = await api.markets.get(id);
      setMarket(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch market");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchMarket();
    const interval = setInterval(fetchMarket, 30000);
    return () => clearInterval(interval);
  }, [fetchMarket]);

  return { market, loading, error, refetch: fetchMarket };
}
