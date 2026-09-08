import type { Metadata } from "next";
import { CartPage } from "@/components/checkout/cart-page";
export const metadata: Metadata = { title: "Panier", robots: { index: false } };
export default function PanierPage() {
  return (
    <div className="border-b border-stone">
      <section className="bg-noir text-paper">
        <div className="container-lux py-10 lg:py-12">
          <p className="eyebrow mb-5 flex items-center gap-3 text-paper/55"><span className="font-display text-lg italic text-champagne-3">Votre panier</span> Étape 1 sur 3</p>
          <h1 className="font-display text-display-lg">Votre sélection, <em className="text-champagne-3">en préparation</em></h1>
          <p className="mt-4 max-w-xl text-sm leading-relaxed text-paper/60">Vérifiez les quantités, ajoutez un message, puis passez à la livraison — le règlement n&apos;intervient qu&apos;à la fin, en toute clarté.</p>
        </div>
      </section>
      <div className="container-lux py-10 lg:py-14"><CartPage /></div>
    </div>
  );
}
