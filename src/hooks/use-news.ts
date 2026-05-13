"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiNewsItem } from "@/lib/api";

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true";

export function useNews(tag?: string) {
  const [news, setNews] = useState<ApiNewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [usingMock, setUsingMock] = useState(false);

  const fetchNews = useCallback(async () => {
    console.log(`[useNews] Fetching news (tag=${tag || "all"})...`);
    try {
      setLoading(true);
      setError(null);
      setUsingMock(false);
      const data = await api.news.list(tag);
      console.log(`[useNews] Got ${data.length} news items from API. First:`, data[0]?.headline || "none");
      setNews(data);
    } catch (err) {
      console.error("[useNews] API fetch failed:", err);
      setError(err instanceof Error ? err : new Error("Failed to fetch news"));
      if (USE_MOCK) {
        console.warn("[useNews] USE_MOCK=true, falling back to mock data");
        const { mockNews } = await import("@/lib/mockApi");
        const filtered = tag
          ? mockNews.filter((n) => n.tags.includes(tag))
          : mockNews;
        console.log(`[useNews] Loaded ${filtered.length} mock news items`);
        setNews(filtered);
        setUsingMock(true);
      } else {
        console.warn("[useNews] USE_MOCK=false, not loading mock data. Array will be empty.");
        setNews([]);
        setUsingMock(false);
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

  return { news, loading, error, usingMock, refetch: fetchNews };
}
