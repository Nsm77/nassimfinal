"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRightIcon } from "@/components/icons";
import { cn } from "@/lib/utils";
const items = [
  { href: "/compte", l: "Vue d'ensemble", d: "Vos dernières commandes et essentiels", n: "01" },
  { href: "/compte/commandes", l: "Mes commandes", d: "Historique, suivi, factures", n: "02" },
  { href: "/compte/favoris", l: "Mes favoris", d: "Votre sélection privée", n: "03" },
  { href: "/compte/profil", l: "Profil & adresses", d: "Informations, sécurité, livraison", n: "04" },
] as const;
export function AccountNav() {
  const p = usePathname();
  return (
    <nav aria-label="Mon espace" className="lg:col-span-3">
      <p className="eyebrow mb-4 hidden lg:block">Mon espace</p>
      <ul className="no-scrollbar-x -mx-5 flex gap-2 overflow-x-auto px-5 pb-1 lg:mx-0 lg:flex-col lg:gap-0 lg:overflow-visible lg:border-y lg:border-stone lg:px-0 lg:pb-0">
        {items.map((it) => {
          const active = it.href === "/compte" ? p === it.href : p.startsWith(it.href);
          return (
            <li key={it.href} className="shrink-0 lg:shrink">
              <Link
                href={it.href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "group relative flex min-h-12 items-center gap-4 px-4 transition-colors duration-300 lg:min-h-[4.5rem] lg:border-b lg:border-stone lg:px-5",
                  active ? "bg-ink text-paper" : "text-charcoal hover:bg-cream hover:text-ink",
                )}
              >
                <span className={cn("hidden font-display text-sm italic lg:block", active ? "text-champagne-3" : "text-muted-2")}>{it.n}</span>
                <span className="flex min-w-0 flex-col">
                  <span className="text-[14px] font-medium">{it.l}</span>
                  <span className={cn("mt-0.5 hidden truncate text-[11px] lg:block", active ? "text-paper/60" : "text-muted-2")}>{it.d}</span>
                </span>
                <ChevronRightIcon size={13} className={cn("ml-auto shrink-0 transition-transform duration-300 lg:hidden", active && "rotate-90")} />
              </Link>
            </li>
          );
        })}
      </ul>
      <div className="mt-6 hidden border border-stone bg-cream p-5 lg:block">
        <p className="eyebrow text-champagne-2">Besoin d&apos;aide ?</p>
        <p className="mt-2 text-xs leading-relaxed text-muted">Nos pharmaciens répondent du lundi au samedi, 8h30–20h30.</p>
        <a href="tel:+21671450210" className="mt-4 inline-flex min-h-10 items-center text-sm font-medium text-ink underline-offset-4 hover:underline">71 450 210</a>
      </div>
    </nav>
  );
}
