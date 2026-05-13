"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiCrossMarket } from "@/lib/api";
import { mockCrossMarket } from "@/lib/mockApi";

export function useCrossMarket() {
  const [comparisons, setComparisons] = useState<ApiCrossMarket[]>([]);
  const [loading, setLoading] = useState(true);
  const [usingMock, setUsingMock] = useState(false);

  const fetchComparisons = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.crossMarket.list();
      setComparisons(data);
      setUsingMock(false);
    } catch {
      setComparisons(mockCrossMarket);
      setUsingMock(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchComparisons();
    const interval = setInterval(fetchComparisons, 30000);
    return () => clearInterval(interval);
  }, [fetchComparisons]);

  return { comparisons, loading, usingMock, refetch: fetchComparisons };
}
