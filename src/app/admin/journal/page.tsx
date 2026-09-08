import { redirect } from "next/navigation";
import { desc } from "drizzle-orm";
import { db } from "@/db";
import { articles } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { AdminPage } from "@/components/admin/ui";
import { ArticlesManager } from "@/components/admin/simple-forms";
export const dynamic = "force-dynamic";
export default async function AdminJournal() {
  if ((await getCurrentUser())?.role !== "admin") redirect("/admin");
  const list = await db.select().from(articles).orderBy(desc(articles.publishedAt));
  return <AdminPage title="Journal" sub={`${list.length} articles`}><ArticlesManager list={list} /></AdminPage>;
}
