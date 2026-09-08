import { notFound, redirect } from "next/navigation";
import { asc, eq } from "drizzle-orm";
import { db } from "@/db";
import { brands, categories, concerns, productConcerns, products } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { AdminPage } from "@/components/admin/ui";
import { ProductForm } from "@/components/admin/product-form";
export const dynamic = "force-dynamic";
export default async function AdminProductEdit({ params }: { params: Promise<{ id: string }> }) {
  const me = await getCurrentUser();
  if (me?.role !== "admin") redirect("/admin");
  const { id } = await params;
  const isNew = id === "nouveau";
  const [product, b, c, k] = await Promise.all([
    isNew ? Promise.resolve(undefined) : db.query.products.findFirst({ where: eq(products.id, Number(id)) }),
    db.select().from(brands).orderBy(asc(brands.name)), db.select().from(categories).orderBy(asc(categories.sortOrder)), db.select().from(concerns).orderBy(asc(concerns.name)),
  ]);
  if (!isNew && !product) notFound();
  const sel = product ? (await db.select({ id: productConcerns.concernId }).from(productConcerns).where(eq(productConcerns.productId, product.id))).map((x) => x.id) : [];
  return (<AdminPage title={isNew ? "Nouveau produit" : product!.name} sub={product ? `SKU ${product.sku}` : undefined}><ProductForm product={product ?? undefined} brands={b} categories={c} concerns={k} selectedConcerns={sel} /></AdminPage>);
}
