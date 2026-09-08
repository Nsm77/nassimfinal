import { NextResponse, type NextRequest } from "next/server";
import { quickSearch } from "@/lib/catalog";

export const dynamic = "force-dynamic";
export async function GET(req: NextRequest) {
  const q = req.nextUrl.searchParams.get("q") ?? "";
  if (q.trim().length < 2) return NextResponse.json({ items: [] });
  const items = await quickSearch(q, 6);
  return NextResponse.json({ items }, { headers: { "Cache-Control": "private, max-age=30" } });
}
