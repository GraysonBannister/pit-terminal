import { MarketDetail } from "@/components/market-detail";

// Don't pre-generate static params — markets are dynamic from the live API
export const dynamic = "force-dynamic";

export default async function MarketDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <MarketDetail id={id} />;
}
