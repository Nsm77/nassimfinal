"use client";
import { useActionState, useEffect } from "react";
import { adjustStockAction } from "@/actions/admin";
import { useToast } from "@/components/ui/toaster";
import { AField, abtn, afield } from "./ui";
export function StockForm({ products }: { products: { id: number; name: string; stock: number }[] }) {
  const [state, action, pending] = useActionState(adjustStockAction, null);
  const { toast } = useToast();
  useEffect(() => { if (state) toast({ kind: state.ok ? "success" : "error", title: state.ok ? state.message ?? "" : state.error }); }, [state, toast]);
  return (<form action={action} className="grid gap-3 sm:grid-cols-4"><AField label="Produit"><select name="productId" required className={afield}>{products.map((p) => <option key={p.id} value={p.id}>{p.name} ({p.stock})</option>)}</select></AField><AField label="Quantité (±)"><input name="delta" type="number" required placeholder="+24 ou -2" className={afield} /></AField><AField label="Motif"><input name="reason" required placeholder="Réception fournisseur, casse…" className={afield} /></AField><div className="flex items-end"><button disabled={pending} className={`${abtn} w-full`}>Ajuster</button></div></form>);
}
