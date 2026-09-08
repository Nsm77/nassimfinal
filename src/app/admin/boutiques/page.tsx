import { redirect } from "next/navigation";
import { db } from "@/db";
import { stores } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { AdminPage } from "@/components/admin/ui";
import { StoresManager } from "@/components/admin/simple-forms";
export const dynamic = "force-dynamic";
export default async function AdminStores() {
  if ((await getCurrentUser())?.role !== "admin") redirect("/admin");
  const list = await db.select().from(stores);
  return <AdminPage title="Boutiques" sub={`${list.length} points de vente`}><StoresManager list={list} /></AdminPage>;
}
