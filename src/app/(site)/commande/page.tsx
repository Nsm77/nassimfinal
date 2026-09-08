import type { Metadata } from "next";
import { desc, eq } from "drizzle-orm";
import { db } from "@/db";
import { addresses, stores } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { CheckoutFlow } from "@/components/checkout/checkout-flow";
export const metadata: Metadata = { title: "Commande", robots: { index: false } };
export const dynamic = "force-dynamic";
export default async function CommandePage() {
  const user = await getCurrentUser();
  const [saved, storeRows] = await Promise.all([user ? db.select().from(addresses).where(eq(addresses.userId, user.id)).orderBy(desc(addresses.isDefault)) : Promise.resolve([]), db.select().from(stores).where(eq(stores.isActive, true))]);
  return (
    <div className="border-b border-stone bg-cream/60">
      <div className="container-lux py-8 lg:py-10">
        <p className="eyebrow mb-4 flex items-center gap-3 text-muted"><span className="font-display text-lg italic text-champagne-2">Commande</span> Un dernier regard, puis c&apos;est entre nos mains</p>
        <CheckoutFlow user={user} savedAddresses={saved} stores={storeRows} />
      </div>
    </div>
  );
}
