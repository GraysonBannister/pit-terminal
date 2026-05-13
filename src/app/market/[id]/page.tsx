import { MarketDetail } from "@/components/market-detail";

export function generateStaticParams() {
  return [
    { id: "will-trump-win-2024" },
    { id: "fed-rate-cut-july" },
    { id: "btc-above-100k-2024" },
    { id: "openai-ipo-2024" },
    { id: "olympics-usa-gold" },
    { id: "ukraine-ceasefire-2024" },
    { id: "japan-ldp-election" },
    { id: "eth-etf-approved" },
  ];
}

export default function MarketDetailPage({ params }: { params: { id: string } }) {
  return <MarketDetail id={params.id} />;
}
