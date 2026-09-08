import { redirect } from "next/navigation";
import { desc, eq } from "drizzle-orm";
import { db } from "@/db";
import { categories, promotions } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { AdminPage } from "@/components/admin/ui";
import { PromotionsManager } from "@/components/admin/simple-forms";
export const dynamic = "force-dynamic";
export default async function AdminPromos() {
  if ((await getCurrentUser())?.role !== "admin") redirect("/admin");
  const [list, u] = await Promise.all([db.select().from(promotions).orderBy(desc(promotions.createdAt)), db.select({ id: categories.id, name: categories.name }).from(categories).where(eq(categories.isUniverse, true))]);
  return <AdminPage title="Promotions" sub={`${list.length} codes`}><PromotionsManager promos={list} universes={u} /></AdminPage>;
}
