import Link from "next/link";
import { redirect } from "next/navigation";
import { desc, eq } from "drizzle-orm";
import { db } from "@/db";
import { orders } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { formatDT } from "@/lib/money";
import { formatDate } from "@/lib/utils";
import { ORDER_STATUS_LABELS } from "@/lib/orders";
import { Badge, EmptyState } from "@/components/ui/primitives";
import { PackageIcon } from "@/components/icons";
export const dynamic = "force-dynamic";
export default async function CommandesPage() {
  // Do not rely on the layout having redirected: Next.js renders the page
  // alongside it, so an anonymous request would otherwise dereference null.
  const user = await getCurrentUser();
  if (!user) redirect("/connexion?next=/compte/commandes");
  const list = await db.query.orders.findMany({ where: eq(orders.userId, user.id), orderBy: desc(orders.createdAt), with: { items: true } });
  if (!list.length) return <EmptyState icon={<PackageIcon size={22} />} title="Aucune commande" description="Vos commandes apparaîtront ici." action={{ href: "/boutique", label: "Découvrir la boutique" }} />;
  return (
    <div><h2 className="mb-6 font-display text-display-sm text-ink">Mes commandes</h2>
      <ul className="divide-y divide-stone border-y border-stone">{list.map((o) => <li key={o.id}><Link href={`/compte/commandes/${o.number}`} className="flex flex-wrap items-center justify-between gap-4 py-5 hover:bg-cream"><div><p className="text-sm text-ink">{o.number}</p><p className="text-xs text-muted">{formatDate(o.createdAt)} · {o.items.reduce((a, i) => a + i.quantity, 0)} article(s)</p></div><div className="flex items-center gap-4"><Badge tone={o.status === "delivered" ? "success" : o.status === "cancelled" ? "error" : "accent"}>{ORDER_STATUS_LABELS[o.status]}</Badge><span className="text-sm tabular-nums text-ink">{formatDT(o.totalMillimes)}</span></div></Link></li>)}</ul></div>
  );
}
