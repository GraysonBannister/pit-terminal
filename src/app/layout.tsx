import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/sidebar";
import { TooltipProvider } from "@/components/ui/tooltip";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "PIT Terminal — Prediction Intelligence",
  description: "Real-time probability intelligence infrastructure for prediction markets.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-slate-950 text-slate-100`}
      >
        <TooltipProvider>
          <div className="flex h-screen">
            <Sidebar />
            <main className="ml-64 flex-1 overflow-y-auto">
              <div className="mx-auto max-w-7xl p-6">
                {children}
              </div>
            </main>
          </div>
        </TooltipProvider>
      </body>
    </html>
  );
}
