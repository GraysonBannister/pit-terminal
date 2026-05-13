"use client";

import { useEffect, useState } from "react";
import { formatTimeAgo } from "@/lib/data";

export function ClientTime({ iso }: { iso: string }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <span className="text-sm font-medium text-slate-500">—</span>;
  }

  return <span className="text-sm font-medium text-slate-500">{formatTimeAgo(iso)}</span>;
}
