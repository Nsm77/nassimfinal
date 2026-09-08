"use client";
import { useState, useTransition } from "react";
import { cancelOrderAction, requestReturnAction } from "@/actions/checkout";
import { useToast } from "@/components/ui/toaster";
export function OrderActions({ orderId, status }: { orderId: number; status: string }) {
  const [pending, start] = useTransition();
  const [confirm, setConfirm] = useState(false);
  const [reason, setReason] = useState("");
  const { toast } = useToast();
  const canCancel = status === "pending" || status === "confirmed";
  const canReturn = status === "delivered";
  if (!canCancel && !canReturn) return null;
  return (
    <div className="border border-stone bg-cream p-5">
      {canCancel && (confirm ? <div className="flex flex-wrap items-center gap-3 text-sm"><span className="text-charcoal">Annuler cette commande ?</span><button disabled={pending} onClick={() => start(async () => { const r = await cancelOrderAction(orderId); toast({ kind: r.ok ? "success" : "error", title: r.ok ? r.message ?? "" : r.error }); setConfirm(false); })} className="btn-secondary min-h-11 px-4 text-[11px]">Oui, annuler</button><button onClick={() => setConfirm(false)} className="min-h-11 text-muted">Non</button></div>
        : <button onClick={() => setConfirm(true)} className="btn-ghost text-error">Annuler la commande</button>)}
      {canReturn && <form onSubmit={(e) => { e.preventDefault(); start(async () => { const r = await requestReturnAction(orderId, reason); toast({ kind: r.ok ? "success" : "error", title: r.ok ? r.message ?? "" : r.error }); }); }} className="space-y-3"><p className="eyebrow">Demander un retour</p><textarea value={reason} onChange={(e) => setReason(e.target.value)} required minLength={5} rows={2} placeholder="Motif du retour" className="field text-sm" /><button disabled={pending} className="btn-secondary">Envoyer la demande</button></form>}
    </div>
  );
}
