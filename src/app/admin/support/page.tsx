import { desc, ne } from "drizzle-orm";
import { db } from "@/db";
import { supportTickets } from "@/db/schema";
import { formatDateTime } from "@/lib/utils";
import { AdminPage, Panel } from "@/components/admin/ui";
import { TicketReply } from "@/components/admin/inline-actions";
export const dynamic = "force-dynamic";
export default async function AdminSupport() {
  const list = await db.select().from(supportTickets).where(ne(supportTickets.status, "closed")).orderBy(desc(supportTickets.createdAt));
  return (
    <AdminPage title="Support" sub={`${list.length} ticket(s) ouverts`}>
      {list.length === 0 ? <p className="text-sm text-admin-muted">Boîte vide.</p> : <div className="space-y-4">{list.map((t) => <Panel key={t.id} className="p-5"><div className="flex flex-wrap items-center justify-between gap-2"><p>{t.subject}</p><span className="text-xs uppercase tracking-[0.12em] text-admin-muted">{t.status}</span></div><p className="mt-1 text-xs text-admin-muted">{t.name} · {t.email} {t.orderNumber && `· ${t.orderNumber}`} · {formatDateTime(t.createdAt)}</p><p className="mt-3 whitespace-pre-line text-sm">{t.message}</p>{t.reply && <p className="mt-3 border-l-2 border-champagne pl-3 text-sm text-admin-muted">{t.reply}</p>}<div className="mt-4"><TicketReply id={t.id} /></div></Panel>)}</div>}
    </AdminPage>
  );
}
