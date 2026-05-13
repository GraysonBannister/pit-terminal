"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiNarrative } from "@/lib/api";

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true";

export function useNarratives(category?: string) {
  const [narratives, setNarratives] = useState<ApiNarrative[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchNarratives = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.narratives.list(category);
      setNarratives(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Failed to fetch narratives"));
      if (USE_MOCK) {
        const { mockNarratives } = await import("@/lib/mockApi");
        const filtered = category
          ? mockNarratives.filter((n) => n.category === category)
          : mockNarratives;
        setNarratives(filtered.sort((a, b) => b.velocity - a.velocity));
      }
    } finally {
      setLoading(false);
    }
  }, [category]);

  useEffect(() => {
    fetchNarratives();
    const interval = setInterval(fetchNarratives, 30000);
    return () => clearInterval(interval);
  }, [fetchNarratives]);

  return { narratives, loading, error, usingMock: USE_MOCK && !!error, refetch: fetchNarratives };
}
