"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiNewsItem } from "@/lib/api";
import { mockNews } from "@/lib/mockApi";

export function useNews(tag?: string) {
  const [news, setNews] = useState<ApiNewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [usingMock, setUsingMock] = useState(false);

  const fetchNews = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.news.list(tag);
      setNews(data);
      setUsingMock(false);
    } catch {
      const filtered = tag
        ? mockNews.filter((n) => n.tags.includes(tag))
        : mockNews;
      setNews(filtered);
      setUsingMock(true);
    } finally {
      setLoading(false);
    }
  }, [tag]);

  useEffect(() => {
    fetchNews();
    const interval = setInterval(fetchNews, 60000);
    return () => clearInterval(interval);
  }, [fetchNews]);

  return { news, loading, usingMock, refetch: fetchNews };
}
