"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Radar,
  LineChart,
  Newspaper,
  GitCompare,
  Settings,
  Zap,
  Shield,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useMarkets } from "@/hooks/use-markets";

const nav = [
  { name: "Dashboard", href: "/", icon: Radar },
  { name: "Opportunities", href: "/opportunities", icon: Zap },
  { name: "Narratives", href: "/narratives", icon: Newspaper },
  { name: "Cross-Market", href: "/cross-market", icon: GitCompare },
  { name: "Markets", href: "/markets", icon: LineChart },
];

export function Sidebar() {
  const pathname = usePathname();
  const { markets } = useMarkets();

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col border-r border-slate-800 bg-slate-950">
      <div className="flex h-16 items-center gap-3 border-b border-slate-800 px-6">
        <Shield className="h-6 w-6 text-indigo-400" />
        <div>
          <h1 className="text-lg font-bold tracking-tight text-slate-50">
            PIT Terminal
          </h1>
          <p className="text-sm font-medium text-slate-400">
            Prediction Intelligence
          </p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-4 py-6">
        {nav.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-4 py-3 text-base font-medium transition-colors",
                active
                  ? "bg-indigo-500/10 text-indigo-300"
                  : "text-slate-300 hover:bg-slate-900 hover:text-slate-100"
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-slate-800 p-4">
        <button className="flex w-full items-center gap-3 rounded-lg px-4 py-3 text-base font-medium text-slate-300 transition-colors hover:bg-slate-900 hover:text-slate-100">
          <Settings className="h-5 w-5" />
          Settings
        </button>
        <div className="mt-4 rounded-lg border border-slate-800 bg-slate-900/50 p-4">
          <p className="text-sm font-semibold text-slate-400 mb-2">
            Terminal Status
          </p>
          <div className="flex items-center gap-2.5">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-base font-medium text-slate-200">Live Monitoring</span>
          </div>
          <p className="mt-2 text-sm text-slate-500">
            {markets.length} markets tracked
          </p>
        </div>
      </div>
    </aside>
  );
}
