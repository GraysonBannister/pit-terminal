"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiNewsItem } from "@/lib/api";

export function useNews(tag?: string) {
  const [news, setNews] = useState<ApiNewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchNews = useCallback(async () => {
    try {
      setError(null);
      const data = await api.news.list(tag);
      setNews(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch news");
    } finally {
      setLoading(false);
    }
  }, [tag]);

  useEffect(() => {
    fetchNews();
    const interval = setInterval(fetchNews, 60000);
    return () => clearInterval(interval);
  }, [fetchNews]);

  return { news, loading, error, refetch: fetchNews };
}
