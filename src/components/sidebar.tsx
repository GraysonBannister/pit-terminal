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

const nav = [
  { name: "Dashboard", href: "/", icon: Radar },
  { name: "Opportunities", href: "/opportunities", icon: Zap },
  { name: "Narratives", href: "/narratives", icon: Newspaper },
  { name: "Cross-Market", href: "/cross-market", icon: GitCompare },
  { name: "Markets", href: "/markets", icon: LineChart },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col border-r border-slate-800 bg-slate-950">
      <div className="flex h-16 items-center gap-3 border-b border-slate-800 px-6">
        <Shield className="h-6 w-6 text-indigo-400" />
        <div>
          <h1 className="text-sm font-bold tracking-tight text-slate-100">
            PIT Terminal
          </h1>
          <p className="text-[10px] font-medium uppercase tracking-wider text-slate-500">
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
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-indigo-500/10 text-indigo-300"
                  : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-slate-800 p-4">
        <button className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-slate-400 transition-colors hover:bg-slate-900 hover:text-slate-200">
          <Settings className="h-4 w-4" />
          Settings
        </button>
        <div className="mt-4 rounded-md border border-slate-800 bg-slate-900/50 p-3">
          <p className="text-[10px] font-medium uppercase tracking-wider text-slate-500">
            Terminal Status
          </p>
          <div className="mt-2 flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs text-slate-300">Live Monitoring</span>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            8 markets tracked
          </p>
        </div>
      </div>
    </aside>
  );
}
