"use client";
import { useActionState, useEffect, useState, useTransition } from "react";
import { changePasswordAction, deleteAddressAction, saveAddressAction, updateProfileAction } from "@/actions/auth";
import { Field } from "@/components/ui/primitives";
import { useToast } from "@/components/ui/toaster";
import { GOVERNORATES } from "@/lib/tunisia";
import type { Address } from "@/db/schema";
import type { ActionResult } from "@/lib/api";

function useFeedback(state: ActionResult | null) {
  const { toast } = useToast();
  useEffect(() => { if (state) toast({ kind: state.ok ? "success" : "error", title: state.ok ? state.message ?? "Enregistré" : state.error }); }, [state, toast]);
}
export function ProfileForm({ user }: { user: { firstName: string; lastName: string; phone: string | null; email: string } }) {
  const [state, action, pending] = useActionState(updateProfileAction, null);
  useFeedback(state);
  const err = (k: string) => (state && !state.ok ? state.fieldErrors?.[k] : undefined);
  return (
    <form action={action} className="space-y-4"><div className="grid gap-4 sm:grid-cols-2"><Field label="Prénom" error={err("firstName")}><input name="firstName" defaultValue={user.firstName} className="field" /></Field><Field label="Nom" error={err("lastName")}><input name="lastName" defaultValue={user.lastName} className="field" /></Field></div><Field label="E-mail"><input value={user.email} disabled className="field opacity-60" /></Field><Field label="Téléphone" error={err("phone")}><input name="phone" defaultValue={user.phone ?? ""} inputMode="tel" className="field" /></Field><button disabled={pending} className="btn-secondary">Enregistrer</button></form>
  );
}
export function PasswordForm() {
  const [state, action, pending] = useActionState(changePasswordAction, null);
  useFeedback(state);
  const err = (k: string) => (state && !state.ok ? state.fieldErrors?.[k] : undefined);
  return (<form action={action} className="space-y-4"><Field label="Mot de passe actuel" error={err("current")}><input name="current" type="password" autoComplete="current-password" required className="field" /></Field><Field label="Nouveau mot de passe" error={err("next")}><input name="next" type="password" autoComplete="new-password" minLength={8} required className="field" /></Field><button disabled={pending} className="btn-secondary">Modifier</button></form>);
}
export function AddressForm({ address, onDone }: { address?: Address; onDone?: () => void }) {
  const [state, action, pending] = useActionState(saveAddressAction, null);
  useFeedback(state);
  useEffect(() => { if (state?.ok) onDone?.(); }, [state, onDone]);
  const err = (k: string) => (state && !state.ok ? state.fieldErrors?.[k] : undefined);
  return (
    <form action={action} className="space-y-4 border border-stone bg-cream p-5">{address && <input type="hidden" name="id" value={address.id} />}
      <div className="grid gap-4 sm:grid-cols-2"><Field label="Libellé"><input name="label" defaultValue={address?.label ?? "Domicile"} className="field" /></Field><Field label="Nom complet" error={err("fullName")}><input name="fullName" defaultValue={address?.fullName} required className="field" /></Field></div>
      <Field label="Téléphone" error={err("phone")}><input name="phone" defaultValue={address?.phone} inputMode="tel" required className="field" /></Field>
      <Field label="Adresse" error={err("line1")}><input name="line1" defaultValue={address?.line1} required className="field" /></Field>
      <Field label="Complément (facultatif)"><input name="line2" defaultValue={address?.line2 ?? ""} className="field" /></Field>
      <div className="grid gap-4 sm:grid-cols-3"><Field label="Gouvernorat" error={err("governorate")}><select name="governorate" defaultValue={address?.governorate ?? "Ben Arous"} className="field">{GOVERNORATES.map((g) => <option key={g}>{g}</option>)}</select></Field><Field label="Ville" error={err("city")}><input name="city" defaultValue={address?.city} required className="field" /></Field><Field label="Code postal"><input name="postalCode" defaultValue={address?.postalCode ?? ""} inputMode="numeric" className="field" /></Field></div>
      <label className="flex min-h-11 items-center gap-3 text-sm"><input type="checkbox" name="isDefault" defaultChecked={address?.isDefault} className="h-4 w-4 accent-ink" /> Adresse par défaut</label>
      <div className="flex gap-3"><button disabled={pending} className="btn-primary">Enregistrer</button>{onDone && <button type="button" onClick={onDone} className="btn-secondary">Annuler</button>}</div></form>
  );
}
export function AddressList({ addresses }: { addresses: Address[] }) {
  const [editing, setEditing] = useState<number | "new" | null>(null);
  const [pending, start] = useTransition();
  const { toast } = useToast();
  return (
    <div className="space-y-4">
      {addresses.map((a) => editing === a.id ? <AddressForm key={a.id} address={a} onDone={() => setEditing(null)} /> : (
        <div key={a.id} className="flex flex-wrap items-start justify-between gap-4 border border-stone p-5 text-sm"><div><p className="text-ink">{a.label}{a.isDefault && <span className="ml-2 text-[10px] uppercase tracking-[0.14em] text-champagne-2">Par défaut</span>}</p><p className="mt-1 text-charcoal">{a.fullName} · {a.phone}<br />{a.line1}{a.line2 ? `, ${a.line2}` : ""}<br />{a.city}, {a.governorate} {a.postalCode}</p></div><div className="flex gap-4"><button onClick={() => setEditing(a.id)} className="min-h-11 text-muted hover:text-ink">Modifier</button><button disabled={pending} onClick={() => start(async () => { const r = await deleteAddressAction(a.id); toast({ kind: r.ok ? "success" : "error", title: r.ok ? r.message ?? "" : r.error }); })} className="min-h-11 text-muted hover:text-error">Supprimer</button></div></div>
      ))}
      {editing === "new" ? <AddressForm onDone={() => setEditing(null)} /> : <button onClick={() => setEditing("new")} className="btn-secondary">Ajouter une adresse</button>}
    </div>
  );
}
