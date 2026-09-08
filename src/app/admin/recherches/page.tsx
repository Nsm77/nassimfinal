import { desc, eq, sql } from "drizzle-orm";
import { db } from "@/db";
import { searchEvents } from "@/db/schema";
import { AdminPage, Table } from "@/components/admin/ui";
export const dynamic = "force-dynamic";
export default async function AdminSearch() {
  const [top, zero] = await Promise.all([
    db.select({ q: searchEvents.query, n: sql<number>`count(*)::int`, avg: sql<number>`round(avg(results_count))::int` }).from(searchEvents).groupBy(searchEvents.query).orderBy(desc(sql`count(*)`)).limit(30),
    db.select({ q: searchEvents.query, n: sql<number>`count(*)::int` }).from(searchEvents).where(eq(searchEvents.resultsCount, 0)).groupBy(searchEvents.query).orderBy(desc(sql`count(*)`)).limit(30),
  ]);
  return (
    <AdminPage title="Recherches" sub="Ce que vos clients cherchent">
      <div className="grid gap-8 lg:grid-cols-2">
        <div><h2 className="mb-3 text-[10px] uppercase tracking-[0.16em] text-admin-muted">Requêtes populaires</h2><Table head={["Requête", "Occurrences", "Résultats moy."]}>{top.map((r) => <tr key={r.q}><td className="px-4 py-2.5">{r.q}</td><td className="px-4 py-2.5 tabular-nums">{r.n}</td><td className="px-4 py-2.5 tabular-nums">{r.avg}</td></tr>)}</Table>{top.length === 0 && <p className="p-4 text-sm text-admin-muted">Aucune donnée.</p>}</div>
        <div><h2 className="mb-3 text-[10px] uppercase tracking-[0.16em] text-admin-muted">Sans résultat (opportunités)</h2><Table head={["Requête", "Occurrences"]}>{zero.map((r) => <tr key={r.q}><td className="px-4 py-2.5">{r.q}</td><td className="px-4 py-2.5 tabular-nums">{r.n}</td></tr>)}</Table>{zero.length === 0 && <p className="p-4 text-sm text-admin-muted">Aucune donnée.</p>}</div>
      </div>
    </AdminPage>
  );
}
