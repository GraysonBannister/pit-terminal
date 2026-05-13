"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiNewsItem } from "@/lib/api";

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true";

export function useNews(tag?: string) {
  const [news, setNews] = useState<ApiNewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchNews = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.news.list(tag);
      setNews(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Failed to fetch news"));
      if (USE_MOCK) {
        const { mockNews } = await import("@/lib/mockApi");
        const filtered = tag
          ? mockNews.filter((n) => n.tags.includes(tag))
          : mockNews;
        setNews(filtered);
      }
    } finally {
      setLoading(false);
    }
  }, [tag]);

  useEffect(() => {
    fetchNews();
    const interval = setInterval(fetchNews, 60000);
    return () => clearInterval(interval);
  }, [fetchNews]);

  return { news, loading, error, usingMock: USE_MOCK && !!error, refetch: fetchNews };
}
