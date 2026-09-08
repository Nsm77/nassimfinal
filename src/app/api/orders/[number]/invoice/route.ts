import { eq } from "drizzle-orm";
import { NextResponse } from "next/server";
import { db } from "@/db";
import { orders } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { buildInvoicePdf } from "@/lib/invoice-pdf";
import { safeEqual } from "@/lib/orders";
import { clientKey } from "@/lib/origin";
import { rateLimit } from "@/lib/rate-limit";

export const dynamic = "force-dynamic";

/**
 * GET /api/orders/:number/invoice[?k=accessKey | ?e=email]
 *
 * Authorisation mirrors the confirmation/tracking pages: the order number is a
 * reference, not a credential. The PDF is served only to the owning session,
 * staff, the bearer of the per-order access key, or — for legacy orders with
 * no key — a rate-limited number+verified-e-mail match.
 */
export async function GET(req: Request, ctx: { params: Promise<{ number: string }> }) {
  const { number } = await ctx.params;
  const url = new URL(req.url);
  const k = url.searchParams.get("k");
  const email = url.searchParams.get("e")?.trim().toLowerCase();

  const o = await db.query.orders.findFirst({ where: eq(orders.number, number.trim().toUpperCase()), with: { items: true } });
  if (!o) return new NextResponse(null, { status: 404 });

  const user = await getCurrentUser();
  const ownsIt = !!user && (o.userId === user.id || user.role === "admin" || user.role === "support");
  const hasKey = safeEqual(k, o.accessKey);
  let byEmail = false;
  if (!ownsIt && !hasKey && email) {
    if (!(await rateLimit(`invoice:${await clientKey()}`, 10, 600_000))) return new NextResponse(null, { status: 404 });
    byEmail = o.email.toLowerCase() === email;
  }
  if (!ownsIt && !hasKey && !byEmail) return new NextResponse(null, { status: 404 });

  const pdf = buildInvoicePdf(o);
  const filename = `facture-cleopatre-${o.number}.pdf`;
  return new NextResponse(new Uint8Array(pdf), {
    status: 200,
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": `attachment; filename="${filename}"`,
      "Content-Length": String(pdf.length),
      "Cache-Control": "private, no-store",
    },
  });
}
