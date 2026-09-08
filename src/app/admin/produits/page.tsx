import Link from "next/link";
import { and, asc, eq, ilike, or, type SQL } from "drizzle-orm";
import { db } from "@/db";
import { brands, products } from "@/db/schema";
import { formatDT } from "@/lib/money";
import { AdminPage, Table, abtn, abtnGhost, afield } from "@/components/admin/ui";
import { DownloadIcon } from "@/components/icons";
export const dynamic = "force-dynamic";
export default async function AdminProducts({ searchParams }: { searchParams: Promise<{ q?: string; status?: string; low?: string }> }) {
  const { q, status, low } = await searchParams;
  const w: SQL[] = [];
  if (q) w.push(or(ilike(products.name, `%${q}%`), ilike(products.sku, `%${q}%`), ilike(brands.name, `%${q}%`))!);
  if (status === "draft" || status === "active" || status === "archived") w.push(eq(products.status, status));
  if (low === "1") w.push(eq(products.stock, 0));
  const rows = await db.select({ id: products.id, name: products.name, sku: products.sku, price: products.priceMillimes, stock: products.stock, t: products.lowStockThreshold, status: products.status, brand: brands.name }).from(products).leftJoin(brands, eq(brands.id, products.brandId)).where(w.length ? and(...w) : undefined).orderBy(asc(products.name)).limit(300);
  return (
    <AdminPage title="Produits" sub={`${rows.length} affichés`} action={<div className="flex gap-2">
            {/* CSV Route Handler, not a page */}
            {/* eslint-disable-next-line @next/next/no-html-link-for-pages */}
            <a href="/api/admin/export/products" className={abtnGhost}><DownloadIcon size={14} /> CSV</a><Link href="/admin/produits/nouveau" className={abtn}>Nouveau produit</Link></div>}>
      <form className="mb-4 flex flex-wrap gap-2"><input name="q" defaultValue={q} placeholder="Nom, SKU, marque…" className={`${afield} max-w-xs`} /><select name="status" defaultValue={status ?? ""} className={`${afield} max-w-[160px]`}><option value="">Tous statuts</option><option value="active">Actif</option><option value="draft">Brouillon</option><option value="archived">Archivé</option></select><label className="flex items-center gap-2 text-sm"><input type="checkbox" name="low" value="1" defaultChecked={low === "1"} className="h-4 w-4 accent-champagne" /> Rupture</label><button className={abtnGhost}>Filtrer</button></form>
      <Table head={["Produit", "SKU", "Marque", "Prix", "Stock", "Statut"]}>{rows.map((p) => <tr key={p.id} className="hover:bg-admin-panel"><td className="px-4 py-3"><Link href={`/admin/produits/${p.id}`} className="hover:underline">{p.name}</Link></td><td className="px-4 py-3 font-mono text-xs">{p.sku}</td><td className="px-4 py-3 text-admin-muted">{p.brand}</td><td className="px-4 py-3 tabular-nums">{formatDT(p.price)}</td><td className={`px-4 py-3 tabular-nums ${p.stock === 0 ? "text-error" : p.stock <= p.t ? "text-warning" : ""}`}>{p.stock}</td><td className="px-4 py-3 text-xs uppercase tracking-[0.12em] text-admin-muted">{p.status}</td></tr>)}</Table>
    </AdminPage>
  );
}
