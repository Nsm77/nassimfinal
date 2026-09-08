import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import { ToasterProvider } from "@/components/ui/toaster";
import { CartProvider } from "@/components/cart/cart-provider";
import { SITE_NAME, SITE_URL } from "@/lib/env";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: SITE_NAME, template: `%s — Cléopâtre` },
  description:
    "Cléopâtre, maison de santé & de beauté à Ezzahra et Hammam-Lif. Dermo-cosmétique, solaire, cheveux et compléments : des produits authentiques, sélectionnés et conseillés par nos pharmaciens, livrés partout en Tunisie.",
  applicationName: "Cléopâtre",
  category: "beauty",
  openGraph: { type: "website", locale: "fr_TN", siteName: SITE_NAME, images: ["/images/hero.jpg"] },
  twitter: { card: "summary_large_image" },
  robots: { index: true, follow: true },
};
export const viewport: Viewport = { themeColor: "#f2ecdf", width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="fr" dir="ltr">
      <body className="min-h-dvh bg-paper text-charcoal">
        <ToasterProvider>
          <CartProvider>{children}</CartProvider>
        </ToasterProvider>
      </body>
    </html>
  );
}
