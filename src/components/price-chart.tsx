"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { PricePoint } from "@/lib/types";

export function PriceChart({ data }: { data: PricePoint[] }) {
  const chartData = data.map((p) => ({
    time: new Date(p.timestamp).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
    probability: p.probability * 100,
    volume: p.volume,
  }));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="probGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
        <XAxis
          dataKey="time"
          stroke="#475569"
          tick={{ fill: "#64748b", fontSize: 10 }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          stroke="#475569"
          tick={{ fill: "#64748b", fontSize: 10 }}
          tickFormatter={(v: number) => `${v.toFixed(0)}%`}
          tickLine={false}
          axisLine={false}
          domain={[0, 100]}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#0f172a",
            border: "1px solid #1e293b",
            borderRadius: "6px",
            fontSize: "12px",
            color: "#e2e8f0",
          }}
          formatter={(value) => [`${Number(value).toFixed(1)}%`, "Probability"]}
          labelStyle={{ color: "#94a3b8", fontSize: "10px" }}
        />
        <Area
          type="monotone"
          dataKey="probability"
          stroke="#6366f1"
          strokeWidth={2}
          fill="url(#probGrad)"
          dot={false}
          activeDot={{ r: 4, stroke: "#6366f1", strokeWidth: 2, fill: "#0f172a" }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
