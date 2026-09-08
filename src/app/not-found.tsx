import Link from "next/link";
import { ArrowRightIcon } from "@/components/icons";
import { Reveal } from "@/components/motion/reveal";

export default function NotFound() {
  return (
    <div className="relative overflow-hidden bg-noir text-paper">
      <div className="container-lux grid min-h-[78svh] items-center gap-12 py-16 lg:grid-cols-2">
        <div>
          <Reveal>
            <p className="eyebrow mb-6 text-paper/50">Erreur 404</p>
            <p className="font-display text-[7rem] italic leading-none text-paper/15 sm:text-[10rem]">404</p>
            <h1 className="-mt-6 font-display text-display-lg">Cette page s&apos;est <em className="text-champagne-3">égarée</em></h1>
            <p className="mt-5 max-w-md text-[15px] leading-relaxed text-paper/65">Le lien est peut-être ancien, ou le produit n&apos;est plus référencé dans notre sélection. Nos rayons, eux, sont bien ouverts.</p>
            <div className="mt-9 flex flex-wrap gap-3">
              <Link href="/boutique" className="btn-light">Explorer la boutique</Link>
              <Link href="/" className="inline-flex min-h-[52px] items-center justify-center gap-2 border border-paper/40 px-8 text-[11px] font-bold uppercase tracking-[0.2em] text-paper transition-colors hover:border-paper hover:bg-paper hover:text-noir">Retour à l&apos;accueil</Link>
            </div>
          </Reveal>
        </div>
        <Reveal delay={0.15} className="border border-paper/15 bg-noir-2 p-8 lg:p-10">
          <p className="eyebrow mb-6 text-paper/50">Par où continuer ?</p>
          <ul className="divide-y divide-paper/10">
            {[
              { h: "/boutique", t: "La boutique complète", d: "Dermo-cosmétique, solaire, cheveux, compléments" },
              { h: "/univers/visage", t: "Univers Visage", d: "Sérums, hydratants, anti-âge" },
              { h: "/univers/solaire", t: "Univers Solaire", d: "Protection SPF 50+ pour toute la famille" },
              { h: "/besoin/peau-sensible", t: "Par besoin", d: "Peau sensible, sèche, imperfections…" },
              { h: "/journal", t: "Le Journal", d: "Conseils de nos pharmaciens" },
            ].map((x) => (
              <li key={x.h}>
                <Link href={x.h} className="group flex items-center justify-between gap-4 py-4">
                  <span><span className="block font-display text-xl text-paper transition-colors group-hover:text-champagne-3">{x.t}</span><span className="mt-0.5 block text-xs text-paper/45">{x.d}</span></span>
                  <ArrowRightIcon size={16} className="shrink-0 text-paper/30 transition-all duration-300 group-hover:translate-x-1 group-hover:text-champagne-3" />
                </Link>
              </li>
            ))}
          </ul>
        </Reveal>
      </div>
    </div>
  );
}
