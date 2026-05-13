"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiNarrative } from "@/lib/api";
import { mockNarratives } from "@/lib/mockApi";

export function useNarratives(category?: string) {
  const [narratives, setNarratives] = useState<ApiNarrative[]>([]);
  const [loading, setLoading] = useState(true);
  const [usingMock, setUsingMock] = useState(false);

  const fetchNarratives = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.narratives.list(category);
      setNarratives(data);
      setUsingMock(false);
    } catch {
      const filtered = category
        ? mockNarratives.filter((n) => n.category === category)
        : mockNarratives;
      setNarratives(filtered.sort((a, b) => b.velocity - a.velocity));
      setUsingMock(true);
    } finally {
      setLoading(false);
    }
  }, [category]);

  useEffect(() => {
    fetchNarratives();
    const interval = setInterval(fetchNarratives, 30000);
    return () => clearInterval(interval);
  }, [fetchNarratives]);

  return { narratives, loading, usingMock, refetch: fetchNarratives };
}
