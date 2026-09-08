import Link from "next/link";
import { notFound } from "next/navigation";
import { desc, eq } from "drizzle-orm";
import { db } from "@/db";
import { addresses, orders, users } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { formatDT } from "@/lib/money";
import { formatDate } from "@/lib/utils";
import { AdminPage, Panel, StatusBadge, Table } from "@/components/admin/ui";
import { CustomerNote, RoleSelect } from "@/components/admin/inline-actions";
export const dynamic = "force-dynamic";
export default async function AdminClient({ params }: { params: Promise<{ id: string }> }) {
  const id = Number((await params).id);
  const [me, u, addr, ords] = await Promise.all([getCurrentUser(), db.query.users.findFirst({ where: eq(users.id, id) }), db.select().from(addresses).where(eq(addresses.userId, id)), db.select().from(orders).where(eq(orders.userId, id)).orderBy(desc(orders.createdAt))]);
  if (!u) notFound();
  return (
    <AdminPage title={`${u.firstName} ${u.lastName}`} sub={u.email} action={me?.role === "admin" ? <RoleSelect userId={u.id} role={u.role} /> : undefined}>
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2"><Table head={["N°", "Total", "Statut", "Date"]}>{ords.map((o) => <tr key={o.id}><td className="px-4 py-3"><Link href={`/admin/commandes/${o.id}`} className="font-mono text-xs hover:underline">{o.number}</Link></td><td className="px-4 py-3 tabular-nums">{formatDT(o.totalMillimes)}</td><td className="px-4 py-3"><StatusBadge s={o.status} /></td><td className="px-4 py-3 text-xs text-admin-muted">{formatDate(o.createdAt)}</td></tr>)}</Table>{ords.length === 0 && <p className="p-4 text-sm text-admin-muted">Aucune commande.</p>}</div>
        <div className="space-y-6">
          <Panel className="p-5 text-sm"><h2 className="mb-3 text-[10px] uppercase tracking-[0.16em] text-admin-muted">Profil</h2><p>{u.phone ?? "—"}</p><p className="text-admin-muted">Inscrit le {formatDate(u.createdAt)}</p><p className="mt-2">{u.loyaltyPoints} points fidélité</p></Panel>
          <Panel className="p-5 text-sm"><h2 className="mb-3 text-[10px] uppercase tracking-[0.16em] text-admin-muted">Adresses</h2>{addr.length === 0 ? <p className="text-admin-muted">Aucune.</p> : <ul className="space-y-3">{addr.map((a) => <li key={a.id}><p>{a.label}</p><p className="text-admin-muted">{a.line1}, {a.city}, {a.governorate}</p></li>)}</ul>}</Panel>
          <Panel className="p-5"><h2 className="mb-3 text-[10px] uppercase tracking-[0.16em] text-admin-muted">Notes internes</h2><CustomerNote userId={u.id} notes={u.notes ?? ""} /></Panel>
        </div>
      </div>
    </AdminPage>
  );
}
