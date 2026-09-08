"use client";
import { useActionState, useEffect, useState } from "react";
import { StarPicker } from "@/components/ui/stars";
import { Field } from "@/components/ui/primitives";
import { useToast } from "@/components/ui/toaster";
import { submitReviewAction } from "@/actions/shop";

export function ReviewForm({ productId, defaultName }: { productId: number; defaultName: string }) {
  const [rating, setRating] = useState(5);
  const [state, action, pending] = useActionState(submitReviewAction, null);
  const { toast } = useToast();
  useEffect(() => { if (state?.ok) toast({ kind: "success", title: state.message ?? "Merci" }); }, [state, toast]);
  if (state?.ok) return <p className="border border-stone bg-cream p-5 text-sm text-charcoal">{state.message}</p>;
  return (
    <form action={action} className="space-y-4 border border-stone bg-cream p-5 sm:p-6">
      <input type="hidden" name="productId" value={productId} /><input type="hidden" name="rating" value={rating} />
      <p className="eyebrow">Votre avis</p>
      <StarPicker value={rating} onChange={setRating} />
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Votre nom" error={state && !state.ok ? state.fieldErrors?.authorName : undefined}><input name="authorName" defaultValue={defaultName} required className="field" /></Field>
        <Field label="Titre (facultatif)"><input name="title" className="field" /></Field>
      </div>
      <Field label="Votre expérience" error={state && !state.ok ? state.fieldErrors?.body : undefined}><textarea name="body" rows={4} required minLength={10} className="field" /></Field>
      {state && !state.ok && <p className="text-xs text-error" role="alert">{state.error}</p>}
      <button disabled={pending} className="btn-secondary">{pending ? "Envoi…" : "Publier mon avis"}</button>
      <p className="text-xs text-muted-2">Les avis sont modérés avant publication.</p>
    </form>
  );
}
