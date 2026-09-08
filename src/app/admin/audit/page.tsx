import { redirect } from "next/navigation";
import { desc, eq } from "drizzle-orm";
import { db } from "@/db";
import { auditLogs, users } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { formatDateTime } from "@/lib/utils";
import { AdminPage, Table } from "@/components/admin/ui";
export const dynamic = "force-dynamic";
export default async function AdminAudit() {
  if ((await getCurrentUser())?.role !== "admin") redirect("/admin");
  const rows = await db.select({ a: auditLogs, actor: users.email }).from(auditLogs).leftJoin(users, eq(users.id, auditLogs.actorId)).orderBy(desc(auditLogs.createdAt)).limit(200);
  return (<AdminPage title="Journal d'audit" sub="200 dernières actions"><Table head={["Date", "Acteur", "Action", "Entité", "Détails"]}>{rows.map(({ a, actor }) => <tr key={a.id}><td className="px-4 py-2.5 text-xs text-admin-muted">{formatDateTime(a.createdAt)}</td><td className="px-4 py-2.5 text-xs">{actor ?? "système"}</td><td className="px-4 py-2.5 font-mono text-xs">{a.action}</td><td className="px-4 py-2.5 text-xs">{a.entity} #{a.entityId}</td><td className="max-w-xs truncate px-4 py-2.5 font-mono text-[11px] text-admin-muted">{JSON.stringify(a.details)}</td></tr>)}</Table>{rows.length === 0 && <p className="p-4 text-sm text-admin-muted">Aucune entrée.</p>}</AdminPage>);
}
