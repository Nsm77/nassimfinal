"use client";
import { useActionState, useEffect, useState } from "react";
import { saveArticleAction, savePromotionAction, saveStoreAction } from "@/actions/admin";
import { useToast } from "@/components/ui/toaster";
import type { Article, Promotion, Store } from "@/db/schema";
import type { ActionResult } from "@/lib/api";
import { AField, abtn, abtnGhost, afield } from "./ui";

function useFb(state: ActionResult | null, onOk?: () => void) {
  const { toast } = useToast();
  useEffect(() => { if (state) { toast({ kind: state.ok ? "success" : "error", title: state.ok ? state.message ?? "" : state.error }); if (state.ok) onOk?.(); } }, [state, toast, onOk]);
}
export function PromotionForm({ promo, universes, onDone }: { promo?: Promotion; universes: { id: number; name: string }[]; onDone?: () => void }) {
  const [state, action, pending] = useActionState(savePromotionAction, null);
  useFb(state, onDone);
  const err = (k: string) => (state && !state.ok ? state.fieldErrors?.[k] : undefined);
  return (
    <form action={action} className="grid gap-3 border border-admin-border bg-admin-panel p-4 sm:grid-cols-4">{promo && <input type="hidden" name="id" value={promo.id} />}
      <AField label="Code" error={err("code")}><input name="code" defaultValue={promo?.code} required className={`${afield} font-mono uppercase`} /></AField>
      <AField label="Libellé" error={err("label")}><input name="label" defaultValue={promo?.label} required className={afield} /></AField>
      <AField label="Type"><select name="type" defaultValue={promo?.type ?? "percent"} className={afield}><option value="percent">Pourcentage</option><option value="fixed">Montant fixe (DT)</option><option value="free_shipping">Livraison offerte</option></select></AField>
      <AField label="Valeur (% ou DT)"><input name="value" type="number" step="0.001" min="0" defaultValue={promo ? (promo.type === "fixed" ? promo.value / 1000 : promo.value) : 10} className={afield} /></AField>
      <AField label="Minimum d'achat (DT)"><input name="minDT" type="number" step="0.001" min="0" defaultValue={promo ? promo.minSubtotalMillimes / 1000 : 0} className={afield} /></AField>
      <AField label="Remise max (DT)"><input name="maxDT" type="number" step="0.001" min="0" defaultValue={promo?.maxDiscountMillimes ? promo.maxDiscountMillimes / 1000 : ""} className={afield} /></AField>
      <AField label="Limite globale"><input name="usageLimit" type="number" min="0" defaultValue={promo?.usageLimit ?? ""} className={afield} /></AField>
      <AField label="Limite / client (0 = illimité)"><input name="perUserLimit" type="number" min="0" defaultValue={promo?.perUserLimit ?? 1} className={afield} /></AField>
      <AField label="Univers (facultatif)"><select name="universeId" defaultValue={promo?.universeId ?? ""} className={afield}><option value="">Tous</option>{universes.map((u) => <option key={u.id} value={u.id}>{u.name}</option>)}</select></AField>
      <AField label="Fin de validité"><input name="endsAt" type="date" defaultValue={promo?.endsAt ? new Date(promo.endsAt).toISOString().slice(0, 10) : ""} className={afield} /></AField>
      <label className="flex min-h-11 items-center gap-2 self-end text-sm"><input type="checkbox" name="isActive" defaultChecked={promo?.isActive ?? true} className="h-4 w-4 accent-champagne" /> Active</label>
      <div className="flex items-end gap-2"><button disabled={pending} className={abtn}>Enregistrer</button>{onDone && <button type="button" onClick={onDone} className={abtnGhost}>Annuler</button>}</div>
    </form>
  );
}
export function PromotionsManager({ promos, universes }: { promos: Promotion[]; universes: { id: number; name: string }[] }) {
  const [editing, setEditing] = useState<number | "new" | null>(null);
  return (
    <div className="space-y-6">
      {editing === "new" ? <PromotionForm universes={universes} onDone={() => setEditing(null)} /> : <button onClick={() => setEditing("new")} className={abtn}>Nouvelle promotion</button>}
      <div className="space-y-2">{promos.map((p) => editing === p.id ? <PromotionForm key={p.id} promo={p} universes={universes} onDone={() => setEditing(null)} /> : (
        <div key={p.id} className="flex flex-wrap items-center justify-between gap-3 border border-admin-border px-4 py-3 text-sm"><div><span className="font-mono">{p.code}</span><span className="ml-3 text-admin-muted">{p.label}</span></div><div className="flex items-center gap-4 text-xs text-admin-muted"><span>{p.usageCount}{p.usageLimit ? `/${p.usageLimit}` : ""} utilisations</span><span className={p.isActive ? "text-success" : "text-error"}>{p.isActive ? "Active" : "Inactive"}</span><button onClick={() => setEditing(p.id)} className="text-admin-text hover:underline">Modifier</button><DeleteSlot id={p.id} /></div></div>
      ))}</div>
    </div>
  );
}
import { DeletePromo } from "./inline-actions";
function DeleteSlot({ id }: { id: number }) { return <DeletePromo id={id} />; }

export function ArticleForm({ article, onDone }: { article?: Article; onDone?: () => void }) {
  const [state, action, pending] = useActionState(saveArticleAction, null);
  useFb(state, onDone);
  return (
    <form action={action} className="grid gap-3 border border-admin-border bg-admin-panel p-4">{article && <input type="hidden" name="id" value={article.id} />}
      <div className="grid gap-3 sm:grid-cols-3"><AField label="Titre"><input name="title" defaultValue={article?.title} required className={afield} /></AField><AField label="Slug"><input name="slug" defaultValue={article?.slug} placeholder="auto" className={afield} /></AField><AField label="Rubrique"><input name="tag" defaultValue={article?.tag ?? ""} className={afield} /></AField></div>
      <div className="grid gap-3 sm:grid-cols-2"><AField label="Extrait"><input name="excerpt" defaultValue={article?.excerpt ?? ""} className={afield} /></AField><AField label="Image (URL)"><input name="image" defaultValue={article?.image ?? ""} className={afield} /></AField></div>
      <AField label="Contenu (paragraphes séparés par une ligne vide)"><textarea name="body" rows={8} defaultValue={article?.body} required className={afield} /></AField>
      <label className="flex min-h-11 items-center gap-2 text-sm"><input type="checkbox" name="isPublished" defaultChecked={article?.isPublished ?? true} className="h-4 w-4 accent-champagne" /> Publié</label>
      <div className="flex gap-2"><button disabled={pending} className={abtn}>Enregistrer</button>{onDone && <button type="button" onClick={onDone} className={abtnGhost}>Annuler</button>}</div>
    </form>
  );
}
export function ArticlesManager({ list }: { list: Article[] }) {
  const [editing, setEditing] = useState<number | "new" | null>(null);
  return (<div className="space-y-6">{editing === "new" ? <ArticleForm onDone={() => setEditing(null)} /> : <button onClick={() => setEditing("new")} className={abtn}>Nouvel article</button>}<div className="space-y-2">{list.map((a) => editing === a.id ? <ArticleForm key={a.id} article={a} onDone={() => setEditing(null)} /> : <div key={a.id} className="flex flex-wrap items-center justify-between gap-3 border border-admin-border px-4 py-3 text-sm"><div>{a.title}<span className="ml-3 text-xs text-admin-muted">{a.tag} · /journal/{a.slug}</span></div><div className="flex items-center gap-4 text-xs"><span className={a.isPublished ? "text-success" : "text-admin-muted"}>{a.isPublished ? "Publié" : "Brouillon"}</span><button onClick={() => setEditing(a.id)} className="hover:underline">Modifier</button></div></div>)}</div></div>);
}
export function StoreForm({ store, onDone }: { store?: Store; onDone?: () => void }) {
  const [state, action, pending] = useActionState(saveStoreAction, null);
  useFb(state, onDone);
  return (
    <form action={action} className="grid gap-3 border border-admin-border bg-admin-panel p-4 sm:grid-cols-3">{store && <input type="hidden" name="id" value={store.id} />}
      <AField label="Nom"><input name="name" defaultValue={store?.name} required className={afield} /></AField><AField label="Slug"><input name="slug" defaultValue={store?.slug} className={afield} /></AField><AField label="Ville"><input name="city" defaultValue={store?.city} required className={afield} /></AField>
      <AField label="Adresse"><input name="address" defaultValue={store?.address} required className={afield} /></AField><AField label="Téléphone"><input name="phone" defaultValue={store?.phone} required className={afield} /></AField><AField label="Horaires"><input name="hours" defaultValue={store?.hours} required className={afield} /></AField>
      <AField label="Lien Maps"><input name="mapsUrl" defaultValue={store?.mapsUrl ?? ""} className={afield} /></AField>
      <label className="flex min-h-11 items-center gap-2 self-end text-sm"><input type="checkbox" name="isActive" defaultChecked={store?.isActive ?? true} className="h-4 w-4 accent-champagne" /> Active</label>
      <div className="flex items-end gap-2"><button disabled={pending} className={abtn}>Enregistrer</button>{onDone && <button type="button" onClick={onDone} className={abtnGhost}>Annuler</button>}</div>
    </form>
  );
}
export function StoresManager({ list }: { list: Store[] }) {
  const [editing, setEditing] = useState<number | "new" | null>(null);
  return (<div className="space-y-6">{editing === "new" ? <StoreForm onDone={() => setEditing(null)} /> : <button onClick={() => setEditing("new")} className={abtn}>Nouvelle boutique</button>}<div className="space-y-2">{list.map((s) => editing === s.id ? <StoreForm key={s.id} store={s} onDone={() => setEditing(null)} /> : <div key={s.id} className="flex flex-wrap items-center justify-between gap-3 border border-admin-border px-4 py-3 text-sm"><div>{s.name}<span className="ml-3 text-xs text-admin-muted">{s.address} · {s.phone}</span></div><div className="flex items-center gap-4 text-xs"><span className={s.isActive ? "text-success" : "text-admin-muted"}>{s.isActive ? "Active" : "Inactive"}</span><button onClick={() => setEditing(s.id)} className="hover:underline">Modifier</button></div></div>)}</div></div>);
}
