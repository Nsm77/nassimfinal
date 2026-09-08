import Link from "next/link";
import { desc, ilike, or, sql } from "drizzle-orm";
import { db } from "@/db";
import { orders, users } from "@/db/schema";
import { formatDT } from "@/lib/money";
import { formatDate } from "@/lib/utils";
import { AdminPage, Table, abtnGhost, afield } from "@/components/admin/ui";
import { DownloadIcon } from "@/components/icons";
export const dynamic = "force-dynamic";
export default async function AdminClients({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const { q } = await searchParams;
  const rows = await db.select({ id: users.id, email: users.email, first: users.firstName, last: users.lastName, phone: users.phone, role: users.role, at: users.createdAt, n: sql<number>`count(${orders.id})::int`, spent: sql<number>`coalesce(sum(${orders.totalMillimes}) filter (where ${orders.status} <> 'cancelled'),0)::int` })
    .from(users).leftJoin(orders, sql`${orders.userId} = ${users.id}`).where(q ? or(ilike(users.email, `%${q}%`), ilike(users.firstName, `%${q}%`), ilike(users.lastName, `%${q}%`), ilike(users.phone, `%${q}%`)) : undefined).groupBy(users.id).orderBy(desc(users.createdAt)).limit(300);
  return (
    <AdminPage title="Clients" sub={`${rows.length} affichés`} action={
      // CSV Route Handler (Content-Disposition: attachment), not a page.
      // eslint-disable-next-line @next/next/no-html-link-for-pages
      <a href="/api/admin/export/customers" className={abtnGhost}><DownloadIcon size={14} /> CSV</a>}>
      <form className="mb-4 flex gap-2"><input name="q" defaultValue={q} placeholder="Nom, e-mail, téléphone…" className={`${afield} max-w-xs`} /><button className={abtnGhost}>Rechercher</button></form>
      <Table head={["Client", "Contact", "Rôle", "Commandes", "Total", "Inscrit"]}>{rows.map((u) => <tr key={u.id} className="hover:bg-admin-panel"><td className="px-4 py-3"><Link href={`/admin/clients/${u.id}`} className="hover:underline">{u.first} {u.last}</Link></td><td className="px-4 py-3 text-xs text-admin-muted">{u.email}<br />{u.phone}</td><td className="px-4 py-3 text-xs uppercase tracking-[0.12em]">{u.role}</td><td className="px-4 py-3 tabular-nums">{u.n}</td><td className="px-4 py-3 tabular-nums">{formatDT(u.spent)}</td><td className="px-4 py-3 text-xs text-admin-muted">{formatDate(u.at)}</td></tr>)}</Table>
    </AdminPage>
  );
}
