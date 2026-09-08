import { NextResponse, type NextRequest } from "next/server";
import { getByIds } from "@/lib/catalog";
export const dynamic = "force-dynamic";
export async function GET(req: NextRequest) {
  const ids = (req.nextUrl.searchParams.get("ids") ?? "").split(",").map(Number).filter((n) => Number.isInteger(n) && n > 0).slice(0, 12);
  return NextResponse.json({ items: await getByIds(ids) });
}
