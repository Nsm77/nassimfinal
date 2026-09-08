import type { ReactNode } from "react";
import { eq, sql } from "drizzle-orm";
import { db } from "@/db";
import { stores, wishlistItems } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { getFeatured, getUniverses } from "@/lib/catalog";
import { Header } from "@/components/shell/header";
import { Footer } from "@/components/shell/footer";
import { CartDrawer } from "@/components/shell/cart-drawer";

export default async function SiteLayout({ children }: { children: ReactNode }) {
  const [universes, user, storeRows, upsells] = await Promise.all([getUniverses(), getCurrentUser(), db.select().from(stores).where(eq(stores.isActive, true)), getFeatured(6)]);
  const wishlistCount = user ? ((await db.select({ n: sql<number>`count(*)::int` }).from(wishlistItems).where(eq(wishlistItems.userId, user.id)))[0]?.n ?? 0) : 0;
  const nav = universes.map((u) => ({ id: u.id, slug: u.slug, name: u.name, description: u.description, image: u.image, children: u.children.map((c) => ({ id: c.id, slug: c.slug, name: c.name })) }));
  return (
    <div className="flex min-h-dvh flex-col">
      <Header universes={nav} user={user} wishlistCount={wishlistCount} />
      <main id="contenu" className="flex-1">{children}</main>
      <Footer universes={nav} stores={storeRows} />
      <CartDrawer upsells={upsells} />
    </div>
  );
}
