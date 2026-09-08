import Link from "next/link";
import { redirect } from "next/navigation";
import { and, desc, eq, gte, sql } from "drizzle-orm";
import { db } from "@/db";
import { orders, products, reviews, supportTickets } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { formatDT } from "@/lib/money";
import { formatDateTime, formatDate } from "@/lib/utils";
import { AdminPage, KPI, Panel, StatusBadge, Table, SectionLabel, abtnGhost } from "@/components/admin/ui";
import { DownloadIcon, PackageIcon, PlusIcon, StarIcon, ChatIcon } from "@/components/icons";
export const dynamic = "force-dynamic";
export default async function AdminDashboard() {
  // Do not rely on the layout having redirected: Next.js renders the page
  // alongside it, so an anonymous request would otherwise dereference null.
  const user = await getCurrentUser();
  if (!user) redirect("/connexion?next=/admin");
  // This is a force-dynamic Server Component; Date.now() drives the rolling 30-day window.
  // eslint-disable-next-line react-hooks/purity
  const since = new Date(Date.now() - 30 * 86_400_000);
  const [kpiRow, pendingRow, recent, low, pendingRow2, ticketsRow, lowRow] = await Promise.all([
    db.select({ n: sql<number>`count(*)::int`, rev: sql<number>`coalesce(sum(total_millimes) filter (where status <> 'cancelled'),0)::int`, avg: sql<number>`coalesce(avg(total_millimes) filter (where status <> 'cancelled'),0)::int` }).from(orders).where(gte(orders.createdAt, since)),
    db.select({ n: sql<number>`count(*)::int` }).from(orders).where(eq(orders.status, "pending")),
    db.select().from(orders).orderBy(desc(orders.createdAt)).limit(10),
    db.select({ id: products.id, name: products.name, stock: products.stock, t: products.lowStockThreshold }).from(products).where(sql`${products.stock} <= ${products.lowStockThreshold} AND ${products.status} = 'active'`).orderBy(products.stock).limit(6),
    db.select({ n: sql<number>`count(*)::int` }).from(reviews).where(eq(reviews.status, "pending")),
    db.select({ n: sql<number>`count(*)::int` }).from(supportTickets).where(eq(supportTickets.status, "open")),
    db.select({ n: sql<number>`count(*)::int` }).from(products).where(sql`${products.stock} <= ${products.lowStockThreshold} AND ${products.status} = 'active'`),
  ]);
  const [kpi] = kpiRow, [pendingCount] = pendingRow, [pendingReviews] = pendingRow2, [openTickets] = ticketsRow, [lowCount] = lowRow;
  const date = new Intl.DateTimeFormat("fr-TN", { weekday: "long", day: "numeric", month: "long" }).format(new Date());
  const attention = pendingCount.n + pendingReviews.n + openTickets.n + lowCount.n;
  const isAdmin = user.role === "admin";
  return (
    <AdminPage eyebrow={`Bonjour ${user.firstName} · ${date}`} title="Vue d'ensemble" sub="Ce qui se passe dans la maison, en un regard." action={
      // CSV Route Handler (Content-Disposition: attachment), not a page.
      // eslint-disable-next-line @next/next/no-html-link-for-pages
      <a href="/api/admin/export/orders" className={abtnGhost}><DownloadIcon size={13} /> Exporter les commandes</a>}>
      {/* Quick actions */}
      <div className="mb-8 flex flex-wrap items-center gap-2">
        <span className="mr-1 text-[10px] font-bold uppercase tracking-[0.2em] text-admin-muted">Actions rapides</span>
        <Link href="/admin/produits/nouveau" className="inline-flex min-h-9 items-center gap-1.5 border border-admin-border px-3 text-[10px] font-bold uppercase tracking-[0.14em] text-admin-text transition-colors hover:border-admin-gold hover:text-admin-gold"><PlusIcon size={12} /> Produit</Link>
        <Link href="/admin/commandes" className="inline-flex min-h-9 items-center gap-1.5 border border-admin-border px-3 text-[10px] font-bold uppercase tracking-[0.14em] text-admin-text transition-colors hover:border-admin-gold hover:text-admin-gold"><PackageIcon size={12} /> Commandes</Link>
        <Link href="/admin/avis" className="inline-flex min-h-9 items-center gap-1.5 border border-admin-border px-3 text-[10px] font-bold uppercase tracking-[0.14em] text-admin-text transition-colors hover:border-admin-gold hover:text-admin-gold"><StarIcon size={12} /> Modération</Link>
        <Link href="/admin/support" className="inline-flex min-h-9 items-center gap-1.5 border border-admin-border px-3 text-[10px] font-bold uppercase tracking-[0.14em] text-admin-text transition-colors hover:border-admin-gold hover:text-admin-gold"><ChatIcon size={12} /> Support</Link>
      </div>

      {/* KPI — 30 days */}
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <KPI label="Chiffre d'affaires · 30 j" value={formatDT(kpi.rev)} sub={`${kpi.n} commandes passées`} />
        <KPI label="Panier moyen" value={formatDT(kpi.avg)} sub="30 derniers jours" />
        <KPI label="Commandes à confirmer" value={String(pendingCount.n)} sub={pendingCount.n ? "priorité : appel client" : "tout est confirmé"} tone={pendingCount.n ? "text-warning-soft" : "text-success-soft"} />
        <KPI label="File d'attention" value={String(attention)} sub={`${pendingReviews.n} avis · ${openTickets.n} tickets · ${lowCount.n} stocks bas`} tone={attention ? "text-admin-gold" : "text-success-soft"} />
      </div>

      {/* Attention queue */}
      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        <Panel title="À traiter — commandes" className="p-0">
          {low.length === 0 && pendingCount.n === 0 ? (
            <p className="px-5 py-6 text-sm text-admin-muted">Aucune commande en attente. La file est nette.</p>
          ) : (
            <ul className="divide-y divide-admin-border">
              {recent.filter((o) => o.status === "pending").slice(0, 5).map((o) => (
                <li key={o.id}>
                  <Link href={`/admin/commandes/${o.id}`} className="flex items-center justify-between gap-3 px-5 py-3.5 transition-colors hover:bg-admin-panel-2">
                    <span className="min-w-0"><span className="block truncate font-mono text-xs text-admin-text">{o.number}</span><span className="text-[11px] text-admin-muted">{o.shippingAddress.fullName}</span></span>
                    <span className="flex shrink-0 items-center gap-3"><span className="tabular-nums text-xs">{formatDT(o.totalMillimes)}</span><StatusBadge s={o.status} /></span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
          <Link href="/admin/commandes?status=pending" className="block border-t border-admin-border px-5 py-3 text-[11px] font-bold uppercase tracking-[0.16em] text-admin-gold transition-colors hover:bg-admin-panel-2">Toutes les commandes en attente →</Link>
        </Panel>

        <Panel title="Alertes stock" className="p-0">
          {low.length === 0 ? (
            <p className="px-5 py-6 text-sm text-admin-muted">Aucune rupture imminente.</p>
          ) : (
            <ul className="divide-y divide-admin-border">
              {low.map((p) => (
                <li key={p.id}>
                  <Link href={`/admin/produits/${p.id}`} className="flex items-center justify-between gap-3 px-5 py-3 transition-colors hover:bg-admin-panel-2">
                    <span className="truncate text-[13px] text-admin-text">{p.name}</span>
                    <span className={`shrink-0 rounded-sm px-2 py-0.5 text-xs font-bold tabular-nums ${p.stock === 0 ? "bg-error-soft text-error" : "bg-warning-soft text-warning"}`}>{p.stock === 0 ? "rupture" : `${p.stock} restant(s)`}</span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
          <Link href="/admin/stock" className="block border-t border-admin-border px-5 py-3 text-[11px] font-bold uppercase tracking-[0.16em] text-admin-gold transition-colors hover:bg-admin-panel-2">Gérer l&apos;inventaire →</Link>
        </Panel>

        <Panel title="Modération & support" className="p-0">
          <ul className="divide-y divide-admin-border text-sm">
            <li><Link href="/admin/avis" className="flex items-center justify-between px-5 py-4 transition-colors hover:bg-admin-panel-2"><span className="flex items-center gap-3"><StarIcon size={15} className="text-admin-gold" /> Avis en attente</span><span className="rounded-sm bg-admin-border px-2 py-0.5 text-xs tabular-nums">{pendingReviews.n}</span></Link></li>
            <li><Link href="/admin/support" className="flex items-center justify-between px-5 py-4 transition-colors hover:bg-admin-panel-2"><span className="flex items-center gap-3"><ChatIcon size={15} className="text-admin-gold" /> Tickets ouverts</span><span className="rounded-sm bg-admin-border px-2 py-0.5 text-xs tabular-nums">{openTickets.n}</span></Link></li>
            <li className="px-5 py-4 text-xs leading-relaxed text-admin-muted">{isAdmin ? "Vous disposez des droits complets sur la maison." : "Compte support — accès limité aux contenus sensibles."}</li>
          </ul>
          <Link href={isAdmin ? "/admin/audit" : "/admin/recherches"} className="block border-t border-admin-border px-5 py-3 text-[11px] font-bold uppercase tracking-[0.16em] text-admin-gold transition-colors hover:bg-admin-panel-2">{isAdmin ? "Consulter l'audit →" : "Voir les recherches →"}</Link>
        </Panel>
      </div>

      {/* Recent orders */}
      <div className="mt-8">
        <SectionLabel className="mb-3">Dernières commandes · {formatDate(new Date(), { day: "numeric", month: "long" })}</SectionLabel>
        <Table head={["N°", "Client", "Total", "Statut", "Passée le"]}>
          {recent.map((o) => (
            <tr key={o.id} className="transition-colors hover:bg-admin-panel-2">
              <td className="px-4 py-3"><Link href={`/admin/commandes/${o.id}`} className="font-mono text-xs text-admin-gold hover:underline">{o.number}</Link></td>
              <td className="px-4 py-3">{o.shippingAddress.fullName}</td>
              <td className="px-4 py-3 tabular-nums">{formatDT(o.totalMillimes)}</td>
              <td className="px-4 py-3"><StatusBadge s={o.status} /></td>
              <td className="px-4 py-3 text-xs text-admin-muted">{formatDateTime(o.createdAt)}</td>
            </tr>
          ))}
        </Table>
      </div>
    </AdminPage>
  );
}
