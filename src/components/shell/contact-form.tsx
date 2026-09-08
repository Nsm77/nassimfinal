"use client";
import { useActionState } from "react";
import { Field } from "@/components/ui/primitives";
import { createTicketAction } from "@/actions/shop";
export function ContactForm() {
  const [state, action, pending] = useActionState(createTicketAction, null);
  if (state?.ok) return <div className="border border-stone bg-cream p-6"><p className="font-display text-display-sm text-ink">Message envoyé</p><p className="mt-2 text-sm text-muted">{state.message}</p></div>;
  const err = (k: string) => (state && !state.ok ? state.fieldErrors?.[k] : undefined);
  return (
    <form action={action} className="space-y-4 border border-stone bg-cream p-6">
      <p className="eyebrow">Nous écrire</p>
      <div className="grid gap-4 sm:grid-cols-2"><Field label="Nom" error={err("name")}><input name="name" required className="field" /></Field><Field label="E-mail" error={err("email")}><input name="email" type="email" required className="field" /></Field></div>
      <div className="grid gap-4 sm:grid-cols-2"><Field label="Sujet" error={err("subject")}><input name="subject" required className="field" /></Field><Field label="N° de commande (facultatif)"><input name="orderNumber" placeholder="CL-…" className="field" /></Field></div>
      <Field label="Message" error={err("message")}><textarea name="message" rows={5} required className="field" /></Field>
      {state && !state.ok && <p className="text-xs text-error" role="alert">{state.error}</p>}
      <button disabled={pending} className="btn-primary w-full sm:w-auto">{pending ? "Envoi…" : "Envoyer"}</button>
    </form>
  );
}
