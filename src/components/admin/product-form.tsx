"use client";
import { useActionState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { saveProductAction } from "@/actions/admin";
import { useToast } from "@/components/ui/toaster";
import type { Brand, Category, Concern, Product } from "@/db/schema";
import { AField, abtn, afield } from "./ui";

export function ProductForm({ product, brands, categories, concerns, selectedConcerns }: { product?: Product; brands: Brand[]; categories: Category[]; concerns: Concern[]; selectedConcerns: number[] }) {
  const [state, action, pending] = useActionState(saveProductAction, null);
  const { toast } = useToast();
  const router = useRouter();
  useEffect(() => { if (state) { toast({ kind: state.ok ? "success" : "error", title: state.ok ? state.message ?? "" : state.error }); if (state.ok && !product) router.push(`/admin/produits/${state.data.id}`); } }, [state, toast, router, product]);
  const err = (k: string) => (state && !state.ok ? state.fieldErrors?.[k] : undefined);
  const universes = categories.filter((c) => c.isUniverse);
  const cats = categories.filter((c) => !c.isUniverse);
  return (
    <form action={action} className="grid gap-6 lg:grid-cols-3">
      {product && <input type="hidden" name="id" value={product.id} />}
      <div className="space-y-4 lg:col-span-2">
        <div className="grid gap-4 sm:grid-cols-2"><AField label="Nom" error={err("name")}><input name="name" defaultValue={product?.name} required className={afield} /></AField><AField label="Slug" error={err("slug")}><input name="slug" defaultValue={product?.slug} placeholder="auto" className={afield} /></AField></div>
        <div className="grid gap-4 sm:grid-cols-3"><AField label="SKU" error={err("sku")}><input name="sku" defaultValue={product?.sku} required className={afield} /></AField><AField label="Contenance"><input name="volume" defaultValue={product?.volume ?? ""} className={afield} /></AField><AField label="Image (URL)"><input name="image" defaultValue={product?.image ?? ""} placeholder="/images/u-visage.jpg" className={afield} /></AField></div>
        <AField label="Accroche" error={err("shortDescription")}><input name="shortDescription" defaultValue={product?.shortDescription ?? ""} maxLength={300} className={afield} /></AField>
        <AField label="Description"><textarea name="description" rows={4} defaultValue={product?.description ?? ""} className={afield} /></AField>
        <div className="grid gap-4 sm:grid-cols-2"><AField label="Ingrédients"><textarea name="ingredients" rows={3} defaultValue={product?.ingredients ?? ""} className={afield} /></AField><AField label="Conseils d'utilisation"><textarea name="howToUse" rows={3} defaultValue={product?.howToUse ?? ""} className={afield} /></AField></div>
        <AField label="Besoins"><div className="grid grid-cols-2 gap-1 sm:grid-cols-3">{concerns.map((c) => <label key={c.id} className="flex min-h-10 items-center gap-2 text-sm"><input type="checkbox" name="concernIds" value={c.id} defaultChecked={selectedConcerns.includes(c.id)} className="h-4 w-4 accent-champagne" />{c.name}</label>)}</div></AField>
      </div>
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4"><AField label="Prix (DT)" error={err("priceMillimes")}><input name="priceDT" type="number" step="0.001" min="0" defaultValue={product ? product.priceMillimes / 1000 : ""} required className={afield} /></AField><AField label="Prix barré (DT)"><input name="compareAtDT" type="number" step="0.001" min="0" defaultValue={product?.compareAtMillimes ? product.compareAtMillimes / 1000 : ""} className={afield} /></AField></div>
        <div className="grid grid-cols-2 gap-4"><AField label="Stock" error={err("stock")}><input name="stock" type="number" min="0" defaultValue={product?.stock ?? 0} className={afield} /></AField><AField label="Seuil alerte"><input name="lowStockThreshold" type="number" min="0" defaultValue={product?.lowStockThreshold ?? 5} className={afield} /></AField></div>
        <AField label="Marque"><select name="brandId" defaultValue={product?.brandId ?? ""} className={afield}><option value="">—</option>{brands.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}</select></AField>
        <AField label="Univers"><select name="universeId" defaultValue={product?.universeId ?? ""} className={afield}><option value="">—</option>{universes.map((u) => <option key={u.id} value={u.id}>{u.name}</option>)}</select></AField>
        <AField label="Catégorie"><select name="categoryId" defaultValue={product?.categoryId ?? ""} className={afield}><option value="">—</option>{cats.map((c) => <option key={c.id} value={c.id}>{universes.find((u) => u.id === c.parentId)?.name} › {c.name}</option>)}</select></AField>
        <AField label="Statut"><select name="status" defaultValue={product?.status ?? "active"} className={afield}><option value="draft">Brouillon</option><option value="active">Actif</option><option value="archived">Archivé</option></select></AField>
        <label className="flex min-h-10 items-center gap-2 text-sm"><input type="checkbox" name="isFeatured" defaultChecked={product?.isFeatured} className="h-4 w-4 accent-champagne" /> Mis en avant</label>
        <label className="flex min-h-10 items-center gap-2 text-sm"><input type="checkbox" name="isNew" defaultChecked={product?.isNew} className="h-4 w-4 accent-champagne" /> Nouveauté</label>
        <button disabled={pending} className={`${abtn} w-full`}>{pending ? "Enregistrement…" : "Enregistrer"}</button>
      </div>
    </form>
  );
}
