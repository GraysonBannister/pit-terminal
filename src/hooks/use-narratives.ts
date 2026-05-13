"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiNarrative } from "@/lib/api";

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true";

export function useNarratives(category?: string) {
  const [narratives, setNarratives] = useState<ApiNarrative[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [usingMock, setUsingMock] = useState(false);

  const fetchNarratives = useCallback(async () => {
    console.log(`[useNarratives] Fetching narratives (category=${category || "all"})...`);
    try {
      setLoading(true);
      setError(null);
      setUsingMock(false);
      const data = await api.narratives.list(category);
      console.log(`[useNarratives] Got ${data.length} narratives from API. First:`, data[0]?.topic || "none");
      setNarratives(data);
    } catch (err) {
      console.error("[useNarratives] API fetch failed:", err);
      setError(err instanceof Error ? err : new Error("Failed to fetch narratives"));
      if (USE_MOCK) {
        console.warn("[useNarratives] USE_MOCK=true, falling back to mock data");
        const { mockNarratives } = await import("@/lib/mockApi");
        const filtered = category
          ? mockNarratives.filter((n) => n.category === category)
          : mockNarratives;
        console.log(`[useNarratives] Loaded ${filtered.length} mock narratives`);
        setNarratives(filtered.sort((a, b) => b.velocity - a.velocity));
        setUsingMock(true);
      } else {
        console.warn("[useNarratives] USE_MOCK=false, not loading mock data. Array will be empty.");
        setNarratives([]);
        setUsingMock(false);
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

  return { narratives, loading, error, usingMock, refetch: fetchNarratives };
}
