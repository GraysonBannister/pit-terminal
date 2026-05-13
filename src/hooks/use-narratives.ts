"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiNarrative } from "@/lib/api";

export function useNarratives(category?: string) {
  const [narratives, setNarratives] = useState<ApiNarrative[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchNarratives = useCallback(async () => {
    try {
      setError(null);
      const data = await api.narratives.list(category);
      setNarratives(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch narratives");
    } finally {
      setLoading(false);
    }
  }, [category]);

  useEffect(() => {
    fetchNarratives();
    const interval = setInterval(fetchNarratives, 30000);
    return () => clearInterval(interval);
  }, [fetchNarratives]);

  return { narratives, loading, error, refetch: fetchNarratives };
}
