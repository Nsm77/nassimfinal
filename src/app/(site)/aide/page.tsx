import type { Metadata } from "next";
import Link from "next/link";
import { ContactForm } from "@/components/shell/contact-form";
import { ClockIcon, MailIcon, PhoneIcon } from "@/components/icons";
export const metadata: Metadata = { title: "Aide & FAQ", description: "Questions fréquentes : livraison, paiement, retours, authenticité. Et si besoin, écrivez-nous." };
const FAQ = [
  ["Quels sont les délais de livraison ?", "24 à 48 h sur le Grand Tunis, 48 à 72 h ailleurs en Tunisie. Les commandes passées avant 14 h partent le jour même (hors dimanche)."],
  ["Quels moyens de paiement acceptez-vous ?", "Le paiement à la livraison (espèces), le virement bancaire et prochainement la carte bancaire. Les cartes cadeaux Cléopâtre sont acceptées en ligne et en boutique."],
  ["Les produits sont-ils authentiques ?", "Oui. Nous nous approvisionnons exclusivement auprès des laboratoires et distributeurs officiels en Tunisie. Chaque produit porte son numéro de lot et sa date de péremption."],
  ["Puis-je retirer ma commande en boutique ?", "Oui, choisissez « Click & Collect » lors de la commande. Elle sera prête sous 2 h à Ezzahra ou Hammam-Lif, sans frais."],
  ["Comment retourner un produit ?", "Vous disposez de 7 jours après réception pour demander un retour depuis votre compte, pour tout produit non ouvert. Nous vous recontactons sous 48 h."],
  ["Puis-je annuler ma commande ?", "Oui, tant qu'elle n'est pas en préparation, directement depuis « Mes commandes ». Les articles sont remis en stock immédiatement."],
  ["Que faire en cas de réaction cutanée ?", "Arrêtez le produit et contactez-nous : nos pharmaciens évaluent la situation avec vous. Si nécessaire, consultez un médecin — la peau d'abord."],
];
export default function AidePage() {
  const ld = { "@context": "https://schema.org", "@type": "FAQPage", mainEntity: FAQ.map(([q, a]) => ({ "@type": "Question", name: q, acceptedAnswer: { "@type": "Answer", text: a } })) };
  return (
    <div className="border-b border-stone">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(ld) }} />
      <section className="bg-noir text-paper">
        <div className="container-lux py-12 lg:py-16">
          <p className="eyebrow mb-6 flex items-center gap-3 text-paper/55"><span className="font-display text-lg italic text-champagne-3">Aide</span> Nous sommes là</p>
          <h1 className="font-display text-display-lg">Une question ? <em className="text-champagne-3">Une vraie personne.</em></h1>
          <div className="mt-9 grid gap-px border border-paper/15 bg-paper/15 sm:grid-cols-3">
            <a href="tel:+21671450210" className="flex items-center gap-4 bg-noir-2 px-6 py-5 text-sm transition-colors hover:bg-paper hover:text-noir"><PhoneIcon size={18} className="text-champagne-3" /><span><span className="block font-medium">71 450 210</span><span className="text-xs opacity-60">Lun–Sam 8h30–20h30</span></span></a>
            <a href="mailto:contact@cleopatre.tn" className="flex items-center gap-4 bg-noir-2 px-6 py-5 text-sm transition-colors hover:bg-paper hover:text-noir"><MailIcon size={18} className="text-champagne-3" /><span><span className="block font-medium">contact@cleopatre.tn</span><span className="text-xs opacity-60">réponse sous 24 h ouvrées</span></span></a>
            <Link href="/boutiques" className="flex items-center gap-4 bg-noir-2 px-6 py-5 text-sm transition-colors hover:bg-paper hover:text-noir"><ClockIcon size={18} className="text-champagne-3" /><span><span className="block font-medium">En boutique</span><span className="text-xs opacity-60">Ezzahra · Hammam-Lif</span></span></Link>
          </div>
        </div>
      </section>

      <div className="container-lux grid gap-14 py-14 lg:grid-cols-12 lg:py-20">
        <div className="lg:col-span-7">
          <p className="eyebrow mb-6 flex items-center gap-3"><span className="font-display text-lg italic text-champagne-2">FAQ</span> Questions fréquentes</p>
          <div className="divide-y divide-stone border-y border-stone">
            {FAQ.map(([q, a]) => (
              <details key={q} className="group py-5">
                <summary className="flex min-h-11 cursor-pointer list-none items-center justify-between gap-6 font-display text-[1.2rem] text-ink">
                  {q}<span aria-hidden="true" className="pl-4 font-display text-2xl font-normal text-muted transition-transform duration-500 group-open:rotate-45">+</span>
                </summary>
                <p className="pb-2 pt-2 text-sm leading-[1.8] text-charcoal">{a}</p>
              </details>
            ))}
          </div>
        </div>
        <div className="lg:col-span-5">
          <div className="lg:sticky lg:top-28"><ContactForm /></div>
        </div>
      </div>
    </div>
  );
}
