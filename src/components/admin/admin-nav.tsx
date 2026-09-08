"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BookIcon, BoxesIcon, ChartIcon, ChatIcon, HomeIcon, ListIcon, PackageIcon, SearchIcon, StarIcon, StoreIcon, TagIcon, UsersIcon, ChevronRightIcon } from "@/components/icons";
import { cn } from "@/lib/utils";

type Item = { href: string; l: string; i: typeof HomeIcon; admin?: boolean };
const groups: { label: string; items: Item[] }[] = [
  {
    label: "Pilotage",
    items: [
      { href: "/admin", l: "Vue d'ensemble", i: HomeIcon },
      { href: "/admin/commandes", l: "Commandes", i: PackageIcon },
    ],
  },
  {
    label: "Catalogue",
    items: [
      { href: "/admin/produits", l: "Produits", i: BoxesIcon },
      { href: "/admin/stock", l: "Stock & inventaire", i: ChartIcon },
      { href: "/admin/promotions", l: "Promotions", i: TagIcon, admin: true },
      { href: "/admin/avis", l: "Avis clients", i: StarIcon },
    ],
  },
  {
    label: "Relation client",
    items: [
      { href: "/admin/clients", l: "Clientes & clients", i: UsersIcon },
      { href: "/admin/support", l: "Support", i: ChatIcon },
      { href: "/admin/recherches", l: "Recherches", i: SearchIcon },
    ],
  },
  {
    label: "Contenu & maison",
    items: [
      { href: "/admin/journal", l: "Journal", i: BookIcon, admin: true },
      { href: "/admin/boutiques", l: "Boutiques", i: StoreIcon, admin: true },
    ],
  },
  {
    label: "Conformité",
    items: [{ href: "/admin/audit", l: "Journal d'audit", i: ListIcon, admin: true }],
  },
];

export function AdminNav({ role }: { role: string }) {
  const p = usePathname();
  const isActive = (href: string) => (href === "/admin" ? p === href : p.startsWith(href));
  return (
    <nav aria-label="Administration">
      {/* mobile horizontal */}
      <div className="lg:hidden">
        <ul className="no-scrollbar-x flex gap-1.5 overflow-x-auto pb-1">
          {groups.flatMap((g) => g.items).filter((i) => !i.admin || role === "admin").map((it) => {
            const active = isActive(it.href);
            return (
              <li key={it.href} className="shrink-0">
                <Link href={it.href} aria-current={active ? "page" : undefined} className={cn("flex min-h-10 items-center gap-2 border px-3 text-[11px] font-bold uppercase tracking-[0.12em] transition-colors",
                  active ? "border-admin-gold bg-admin-gold text-noir" : "border-admin-border text-admin-muted hover:text-admin-text")}>
                  <it.i size={13} />{it.l}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
      {/* desktop rail */}
      <div className="hidden space-y-7 lg:block">
        {groups.map((g) => {
          const items = g.items.filter((i) => !i.admin || role === "admin");
          if (!items.length) return null;
          return (
            <div key={g.label}>
              <p className="mb-2 px-3 text-[9px] font-bold uppercase tracking-[0.26em] text-admin-muted/70">{g.label}</p>
              <ul className="space-y-0.5">
                {items.map((it) => {
                  const active = isActive(it.href);
                  return (
                    <li key={it.href}>
                      <Link
                        href={it.href}
                        aria-current={active ? "page" : undefined}
                        className={cn("group relative flex min-h-11 items-center gap-3 px-3 text-[13px] transition-colors duration-200",
                          active ? "bg-admin-gold/10 text-admin-text" : "text-admin-muted hover:bg-admin-panel hover:text-admin-text")}
                      >
                        <span aria-hidden className={cn("absolute inset-y-2 left-0 w-0.5 transition-colors", active ? "bg-admin-gold" : "bg-transparent group-hover:bg-admin-border")} />
                        <it.i size={15} className={cn(active ? "text-admin-gold" : "text-admin-muted")} />
                        {it.l}
                        {active && <ChevronRightIcon size={12} className="ml-auto text-admin-gold" />}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          );
        })}
      </div>
    </nav>
  );
}
