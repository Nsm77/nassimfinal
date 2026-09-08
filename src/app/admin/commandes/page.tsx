import { and, desc, eq, ilike, or, type SQL } from "drizzle-orm";
import { db } from "@/db";
import { orders, orderStatusEnum } from "@/db/schema";
import { ORDER_STATUS_LABELS } from "@/lib/orders";
import { AdminPage, abtnGhost, afield } from "@/components/admin/ui";
import { OrdersTable } from "@/components/admin/orders-table";
import { DownloadIcon } from "@/components/icons";
export const dynamic = "force-dynamic";
export default async function AdminOrders({ searchParams }: { searchParams: Promise<{ q?: string; status?: string }> }) {
  const { q, status } = await searchParams;
  const w: SQL[] = [];
  if (q) w.push(or(ilike(orders.number, `%${q}%`), ilike(orders.email, `%${q}%`), ilike(orders.phone, `%${q}%`), ilike(orders.shippingAddress, `%${q}%`))!);
  if (status && (orderStatusEnum.enumValues as string[]).includes(status)) w.push(eq(orders.status, status as typeof orderStatusEnum.enumValues[number]));
  const rows = await db.select().from(orders).where(w.length ? and(...w) : undefined).orderBy(desc(orders.createdAt)).limit(200);
  return (
    <AdminPage title="Commandes" sub={`${rows.length} affichées`} action={
      // CSV Route Handler (Content-Disposition: attachment), not a page.
      // eslint-disable-next-line @next/next/no-html-link-for-pages
      <a href="/api/admin/export/orders" className={abtnGhost}><DownloadIcon size={14} /> CSV</a>}>
      <form className="mb-4 flex flex-wrap gap-2"><input name="q" defaultValue={q} placeholder="N°, e-mail, téléphone, nom…" className={`${afield} max-w-xs`} /><select name="status" defaultValue={status ?? ""} className={`${afield} max-w-[180px]`}><option value="">Tous statuts</option>{orderStatusEnum.enumValues.map((s) => <option key={s} value={s}>{ORDER_STATUS_LABELS[s]}</option>)}</select><button className={abtnGhost}>Filtrer</button></form>
      <OrdersTable rows={rows} />
    </AdminPage>
  );
}
