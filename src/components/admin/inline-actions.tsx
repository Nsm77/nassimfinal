"use client";
import { useState, useTransition } from "react";
import { deletePromotionAction, moderateReviewAction, replyTicketAction, saveCustomerNoteAction, updateUserRoleAction } from "@/actions/admin";
import { useToast } from "@/components/ui/toaster";
import { abtn, abtnGhost, afield } from "./ui";

function useRun() {
  const [pending, start] = useTransition();
  const { toast } = useToast();
  const run = (fn: () => Promise<{ ok: boolean; message?: string; error?: string }>) => start(async () => { const r = await fn(); toast({ kind: r.ok ? "success" : "error", title: r.ok ? r.message ?? "OK" : r.error ?? "Erreur" }); });
  return { pending, run };
}
export function ReviewActions({ id }: { id: number }) {
  const { pending, run } = useRun();
  const [reply, setReply] = useState("");
  return (<div className="space-y-2"><input value={reply} onChange={(e) => setReply(e.target.value)} placeholder="Réponse publique (facultatif)" className={afield} /><div className="flex gap-2"><button disabled={pending} onClick={() => run(() => moderateReviewAction(id, "approved", reply))} className={abtn}>Publier</button><button disabled={pending} onClick={() => run(() => moderateReviewAction(id, "rejected"))} className={`${abtnGhost} text-error`}>Rejeter</button></div></div>);
}
export function TicketReply({ id }: { id: number }) {
  const { pending, run } = useRun();
  const [reply, setReply] = useState("");
  return (<div className="space-y-2"><textarea value={reply} onChange={(e) => setReply(e.target.value)} rows={3} placeholder="Votre réponse…" className={afield} /><div className="flex gap-2"><button disabled={pending} onClick={() => run(() => replyTicketAction(id, reply, false))} className={abtn}>Répondre</button><button disabled={pending} onClick={() => run(() => replyTicketAction(id, reply, true))} className={abtnGhost}>Répondre & clore</button></div></div>);
}
export function DeletePromo({ id }: { id: number }) {
  const { pending, run } = useRun();
  return <button disabled={pending} onClick={() => confirm("Supprimer cette promotion ?") && run(() => deletePromotionAction(id))} className="text-xs text-error hover:underline">Supprimer</button>;
}
export function RoleSelect({ userId, role }: { userId: number; role: string }) {
  const { pending, run } = useRun();
  return <select disabled={pending} defaultValue={role} onChange={(e) => run(() => updateUserRoleAction(userId, e.target.value as "customer" | "support" | "admin"))} className={`${afield} max-w-[140px]`}><option value="customer">Client</option><option value="support">Support</option><option value="admin">Admin</option></select>;
}
export function CustomerNote({ userId, notes }: { userId: number; notes: string }) {
  const { pending, run } = useRun();
  const [n, setN] = useState(notes);
  return (<div className="space-y-2"><textarea value={n} onChange={(e) => setN(e.target.value)} rows={3} className={afield} placeholder="Notes internes sur ce client" /><button disabled={pending} onClick={() => run(() => saveCustomerNoteAction(userId, n))} className={abtnGhost}>Enregistrer</button></div>);
}
