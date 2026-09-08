"use client";
import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";
import { bulkOrderStatusAction, saveOrderNotesAction, updateOrderStatusAction } from "@/actions/admin";
import { useToast } from "@/components/ui/toaster";
import { ALLOWED_TRANSITIONS, ORDER_STATUS_LABELS } from "@/lib/order-constants";
import type { OrderStatus } from "@/db/schema";
import { abtn, abtnGhost, afield } from "./ui";

export function StatusButtons({ orderId, status }: { orderId: number; status: OrderStatus }) {
  const [pending, start] = useTransition();
  const { toast } = useToast();
  const [msg, setMsg] = useState("");
  const nexts = ALLOWED_TRANSITIONS[status];
  if (!nexts.length) return <p className="text-sm text-admin-muted">Commande clôturée.</p>;
  return (
    <div className="space-y-3"><input value={msg} onChange={(e) => setMsg(e.target.value)} placeholder="Message pour la chronologie (facultatif)" className={afield} />
      <div className="flex flex-wrap gap-2">{nexts.map((n) => <button key={n} disabled={pending} onClick={() => { if ((n === "cancelled" || n === "returned") && !confirm(`Confirmer : ${ORDER_STATUS_LABELS[n]} ? Le stock sera réintégré.`)) return; start(async () => { const r = await updateOrderStatusAction(orderId, n, msg); toast({ kind: r.ok ? "success" : "error", title: r.ok ? r.message ?? "" : r.error }); setMsg(""); }); }} className={n === "cancelled" || n === "returned" ? `${abtnGhost} text-error` : abtn}>{ORDER_STATUS_LABELS[n]}</button>)}</div></div>
  );
}
export function NotesForm({ orderId, internalNote, trackingCode }: { orderId: number; internalNote: string; trackingCode: string }) {
  const [pending, start] = useTransition();
  const { toast } = useToast();
  const [n, setN] = useState(internalNote); const [t, setT] = useState(trackingCode);
  return (<form onSubmit={(e) => { e.preventDefault(); start(async () => { const r = await saveOrderNotesAction(orderId, n, t); toast({ kind: r.ok ? "success" : "error", title: r.ok ? r.message ?? "" : r.error }); }); }} className="space-y-3"><input value={t} onChange={(e) => setT(e.target.value)} placeholder="Code de suivi transporteur" className={afield} /><textarea value={n} onChange={(e) => setN(e.target.value)} rows={3} placeholder="Notes internes (non visibles par le client)" className={afield} /><button disabled={pending} className={abtnGhost}>Enregistrer</button></form>);
}
export function BulkBar({ ids, onDone }: { ids: number[]; onDone: () => void }) {
  const [pending, start] = useTransition();
  const { toast } = useToast();
  const router = useRouter();
  if (!ids.length) return null;
  return (<div className="mb-3 flex flex-wrap items-center gap-2 border border-admin-border bg-admin-panel p-3 text-sm"><span className="text-admin-muted">{ids.length} sélectionnée(s) →</span>{(["confirmed", "preparing", "shipped", "delivered"] as const).map((s) => <button key={s} disabled={pending} onClick={() => start(async () => { const r = await bulkOrderStatusAction(ids, s); toast({ kind: "info", title: r.ok ? r.message ?? "" : r.error }); onDone(); router.refresh(); })} className={abtnGhost}>{ORDER_STATUS_LABELS[s]}</button>)}</div>);
}
