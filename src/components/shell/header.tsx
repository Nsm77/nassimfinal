"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { ArrowRightIcon, CartIcon, ChevronDownIcon, ChevronRightIcon, CloseIcon, HeartIcon, LogoMark, MenuIcon, SearchIcon, UserIcon } from "@/components/icons";
import { useCart } from "@/components/cart/cart-provider";
import type { SafeUser } from "@/lib/auth";
import { EASE_LUXE, tweenExit } from "@/lib/motion";
import { logoutAction } from "@/actions/auth";
import { SearchOverlay } from "./search-overlay";

export type NavUniverse = { id: number; slug: string; name: string; description: string | null; image: string | null; children: { id: number; slug: string; name: string }[] };

function Badge({ n }: { n: number }) {
  const reduce = useReducedMotion();
  return (
    <AnimatePresence>
      {n > 0 && (
        <motion.span
          key={n}
          initial={reduce ? false : { scale: 0.6, opacity: 0 }}
          animate={{ scale: 1, opacity: 1, transition: { type: "spring", stiffness: 260, damping: 22 } }}
          exit={{ scale: 0.6, opacity: 0, transition: tweenExit }}
          className="absolute -right-1 -top-0.5 flex h-[18px] min-w-[18px] items-center justify-center bg-champagne px-1 text-[9px] font-bold tabular-nums text-ink"
        >
          {n}
        </motion.span>
      )}
    </AnimatePresence>
  );
}

export function Header({ universes, user, wishlistCount }: { universes: NavUniverse[]; user: SafeUser | null; wishlistCount: number }) {
  const { count, open } = useCart();
  const [searchOpen, setSearchOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [mega, setMega] = useState<number | null>(null);
  const [scrolled, setScrolled] = useState(false);
  const [acct, setAcct] = useState(false);
  const pathname = usePathname();
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reduce = useReducedMotion();

  // Close the overlays when the route changes (React's adjust-during-render pattern).
  const [prevPath, setPrevPath] = useState(pathname);
  if (prevPath !== pathname) { setPrevPath(pathname); setMenuOpen(false); setMega(null); setAcct(false); }
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); setSearchOpen(true); }
      if (e.key === "Escape") { setMega(null); setAcct(false); setMenuOpen(false); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);
  useEffect(() => { document.body.style.overflow = menuOpen ? "hidden" : ""; return () => { document.body.style.overflow = ""; }; }, [menuOpen]);

  const enter = (id: number) => { if (closeTimer.current) clearTimeout(closeTimer.current); setMega(id); };
  const leave = () => { closeTimer.current = setTimeout(() => setMega(null), 160); };
  const active = universes.find((u) => u.id === mega);

  return (
    <>
      {/* Utility hairline — whisper-thin, never a banner */}
      <div className="relative z-50 border-b border-stone/60 bg-cream text-center">
        <p className="container-lux flex min-h-7 items-center justify-center gap-5 overflow-hidden text-[9.5px] font-semibold tracking-[0.16em] text-muted uppercase">
          <span className="hidden sm:inline">Livraison offerte dès 99&nbsp;DT</span>
          <span aria-hidden="true" className="hidden sm:inline text-stone-2">·</span>
          <span>Paiement à la livraison</span>
          <span aria-hidden="true" className="hidden sm:inline text-stone-2">·</span>
          <span className="hidden sm:inline">Conseils experts 71&nbsp;450&nbsp;210</span>
        </p>
      </div>

      <header
        className={`sticky top-0 z-40 border-b transition-all duration-500 ${scrolled || mega !== null ? "border-stone bg-paper/95 shadow-whisper backdrop-blur-xl" : "border-transparent bg-paper"}`}
        onMouseLeave={leave}
      >
        {/* Main row: wordmark · search · actions */}
        <div className="container-lux grid h-16 grid-cols-[auto_1fr_auto] items-center gap-4 lg:gap-8">
          <div className="flex items-center gap-1 lg:hidden">
            <button onClick={() => setMenuOpen(true)} aria-label="Ouvrir le menu" aria-expanded={menuOpen} className="flex h-11 w-11 items-center justify-center text-ink transition-colors hover:text-champagne-2"><MenuIcon /></button>
          </div>

          <Link href="/" className="group flex items-center gap-3 text-ink" aria-label="Cléopâtre — Espace Santé Beauté, accueil">
            <LogoMark size={30} className="text-champagne-2 transition-colors duration-500 group-hover:text-ink" />
            <span className="flex flex-col leading-none">
              <span className="font-display text-[22px] font-medium tracking-[0.02em] lg:text-[26px]">Cléopâtre</span>
              <span className="mt-1 hidden text-[8px] font-bold uppercase tracking-[0.34em] text-muted sm:block">Espace Santé Beauté</span>
            </span>
          </Link>

          <button
            onClick={() => setSearchOpen(true)}
            className="mx-auto hidden h-11 w-full max-w-md items-center gap-3 border border-stone bg-cream/60 px-4 text-left text-[13px] text-muted transition-colors hover:border-champagne-2 focus:border-champagne-2 lg:flex"
            aria-label="Rechercher un produit, une marque"
          >
            <SearchIcon size={16} /> Rechercher un produit, une marque…
          </button>

          <div className="flex items-center justify-end gap-0.5">
            <div className="relative" onMouseEnter={() => { setMega(null); if (user) setAcct(true); }} onMouseLeave={() => setAcct(false)}>
              <Link href={user ? "/compte" : "/connexion"} aria-label={user ? "Mon compte" : "Se connecter"} className="flex h-11 w-11 items-center justify-center text-ink transition-colors hover:text-champagne-2" onFocus={() => user && setAcct(true)}>
                <UserIcon />
              </Link>
              <AnimatePresence>
                {acct && user && (
                  <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0, transition: { duration: 0.4, ease: EASE_LUXE } }} exit={{ opacity: 0, transition: tweenExit }} className="absolute right-0 top-full w-64 border border-stone bg-cream p-3 shadow-float">
                    <p className="border-b border-stone px-3 pb-3 text-xs text-muted">Bonjour, <span className="font-medium text-ink">{user.firstName} {user.lastName}</span></p>
                    <div className="py-1">
                      {[[user.role === "admin" || user.role === "support" ? "/admin" : "/compte", "Mon espace"], ["/compte/commandes", "Mes commandes"], ["/compte/favoris", "Mes favoris"], ["/compte/profil", "Profil & adresses"]].map(([h, l]) => (
                        <Link key={h} href={h} className="block px-3 py-2.5 text-sm text-charcoal transition-colors hover:bg-paper hover:text-ink">{l}</Link>
                      ))}
                    </div>
                    {(user.role === "admin" || user.role === "support") && <Link href="/admin" className="block border-t border-stone px-3 py-2.5 text-sm text-champagne-2">Administration</Link>}
                    <form action={logoutAction}><button className="block w-full px-3 py-2.5 text-left text-sm text-muted transition-colors hover:bg-paper hover:text-ink">Se déconnecter</button></form>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            <Link href={user ? "/compte/favoris" : "/connexion?next=/compte/favoris"} aria-label="Favoris" className="relative flex h-11 w-11 items-center justify-center text-ink transition-colors hover:text-champagne-2">
              <HeartIcon /><Badge n={wishlistCount} />
            </Link>
            <button onClick={open} aria-label={`Panier, ${count} article${count > 1 ? "s" : ""}`} className="relative flex h-11 w-11 items-center justify-center text-ink transition-colors hover:text-champagne-2">
              <CartIcon /><Badge n={count} />
            </button>
          </div>
        </div>

        {/* Mobile search row — intentional, not a shrunken desktop field */}
        <div className="border-t border-stone/60 px-4 pb-2.5 pt-2 lg:hidden">
          <button onClick={() => setSearchOpen(true)} className="flex h-10 w-full items-center gap-3 border border-stone bg-cream/60 px-4 text-left text-[13px] text-muted transition-colors hover:border-champagne-2" aria-label="Rechercher un produit, une marque">
            <SearchIcon size={15} /> Rechercher un produit, une marque…
          </button>
        </div>

        {/* Primary nav — no numbers, calm editorial row */}
        <nav className="hidden border-t border-stone/70 lg:block" aria-label="Navigation principale">
          <div className="container-lux no-scrollbar-x flex items-center gap-6 overflow-x-auto xl:justify-center xl:gap-8">
            <Link href="/boutique?sort=newest" onMouseEnter={() => setMega(null)} className="whitespace-nowrap py-2.5 text-[12px] font-semibold tracking-[0.14em] text-charcoal uppercase transition-colors hover:text-ink">Nouveautés</Link>
            {universes.map((u) => (
              <Link
                key={u.id}
                href={`/univers/${u.slug}`}
                onMouseEnter={() => enter(u.id)}
                onFocus={() => enter(u.id)}
                aria-expanded={mega === u.id}
                aria-haspopup="true"
                className={`relative whitespace-nowrap py-2.5 text-[12px] font-semibold tracking-[0.14em] uppercase transition-colors ${mega === u.id ? "text-champagne-2" : "text-charcoal hover:text-ink"}`}
              >
                {u.name}
                <span className={`absolute inset-x-0 -bottom-px h-px bg-champagne-2 transition-transform duration-300 ${mega === u.id ? "scale-x-100" : "scale-x-0"}`} />
              </Link>
            ))}
            <Link href="/promotions" onMouseEnter={() => setMega(null)} className="whitespace-nowrap py-2.5 text-[12px] font-semibold tracking-[0.14em] text-champagne-2 uppercase transition-colors hover:text-ink">Offres</Link>
          </div>
        </nav>

        {/* Mega menu */}
        <AnimatePresence>
          {active && (
            <motion.div
              key={active.id}
              initial={reduce ? false : { opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0, transition: { duration: 0.45, ease: EASE_LUXE } }}
              exit={{ opacity: 0, transition: tweenExit }}
              onMouseEnter={() => enter(active.id)}
              className="absolute inset-x-0 top-full hidden border-b border-stone bg-paper/97 shadow-soft backdrop-blur-xl lg:block"
            >
              <div className="container-lux grid grid-cols-12 gap-10 py-10">
                <div className="col-span-8">
                  <div className="grid grid-cols-3 gap-x-10 gap-y-2">
                    {active.children.map((c) => (
                      <Link key={c.id} href={`/categorie/${c.slug}`} className="group flex items-center gap-2 border-b border-stone/50 py-3 text-[14px] text-charcoal transition-colors hover:text-ink">
                        {c.name}
                        <ArrowRightIcon size={12} className="text-champagne-2 opacity-0 transition-opacity group-hover:opacity-100" />
                      </Link>
                    ))}
                  </div>
                  <Link href={`/univers/${active.slug}`} className="btn-secondary mt-7">Tout l&apos;univers {active.name} <ArrowRightIcon size={14} /></Link>
                </div>
                <div className="col-span-4 border-l border-stone pl-10">
                  {active.image && (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={active.image} alt="" className="mb-5 aspect-[4/3] w-full object-cover" />
                  )}
                  <h3 className="font-display text-xl italic text-ink">{active.name}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted">{active.description}</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      {/* Mobile menu */}
      <AnimatePresence>
        {menuOpen && (
          <>
            <motion.button aria-label="Fermer le menu" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.4 }} onClick={() => setMenuOpen(false)} className="fixed inset-0 z-50 bg-ink/40 backdrop-blur-sm lg:hidden" />
            <motion.aside
              role="dialog" aria-modal="true" aria-label="Menu principal"
              initial={reduce ? false : { x: "-100%" }} animate={{ x: 0 }} exit={{ x: "-100%" }}
              transition={{ type: "spring", stiffness: 190, damping: 32 }}
              className="fixed inset-y-0 left-0 z-[60] flex w-[88vw] max-w-md flex-col bg-paper shadow-drawer lg:hidden"
            >
              <div className="flex h-16 items-center justify-between border-b border-stone px-5">
                <span className="font-display text-[22px] text-ink">Cléopâtre</span>
                <button onClick={() => setMenuOpen(false)} aria-label="Fermer le menu" className="flex h-11 w-11 items-center justify-center text-ink"><CloseIcon /></button>
              </div>
              <button onClick={() => { setMenuOpen(false); setSearchOpen(true); }} className="mx-5 mt-4 flex h-12 items-center gap-3 border border-stone bg-cream/60 px-4 text-left text-[14px] text-muted">
                <SearchIcon size={16} /> Rechercher…
              </button>
              <div className="flex-1 overflow-y-auto px-6 py-5">
                <ul className="space-y-0.5">
                  <li><Link href="/boutique?sort=newest" onClick={() => setMenuOpen(false)} className="flex min-h-12 items-center justify-between text-[15px] font-semibold text-champagne-2">Nouveautés <ChevronRightIcon size={14} /></Link></li>
                  {universes.map((u) => (
                    <li key={u.id}>
                      <details className="group border-b border-stone/70">
                        <summary className="flex min-h-13 cursor-pointer list-none items-center justify-between py-3.5 text-[16px] text-ink">
                          {u.name}
                          <ChevronDownIcon size={17} className="text-muted transition-transform duration-500 group-open:rotate-180" />
                        </summary>
                        <ul className="mb-4 space-y-0.5">
                          <li><Link href={`/univers/${u.slug}`} onClick={() => setMenuOpen(false)} className="flex min-h-11 items-center justify-between pl-2 text-[15px] font-medium text-champagne-2">Tout {u.name} <ArrowRightIcon size={13} /></Link></li>
                          {u.children.map((c) => <li key={c.id}><Link href={`/categorie/${c.slug}`} onClick={() => setMenuOpen(false)} className="block min-h-11 pl-2 text-[15px] text-charcoal">{c.name}</Link></li>)}
                        </ul>
                      </details>
                    </li>
                  ))}
                  <li><Link href="/promotions" onClick={() => setMenuOpen(false)} className="flex min-h-12 items-center justify-between text-[15px] font-semibold text-champagne-2">Offres <ChevronRightIcon size={14} /></Link></li>
                </ul>
                <div className="mt-4 grid grid-cols-2 gap-x-4">
                  {([
                    { href: user ? "/compte" : "/connexion", label: "Mon compte", icon: UserIcon },
                    { href: user ? "/compte/favoris" : "/connexion?next=/compte/favoris", label: "Favoris", icon: HeartIcon },
                  ]).map(({ href, label, icon: Icon }) => (
                    <Link key={label} href={href} onClick={() => setMenuOpen(false)} className="flex min-h-13 items-center gap-3 border border-stone px-4 text-[12px] font-bold uppercase tracking-[0.1em] text-ink">
                      <Icon size={16} /> {label}
                    </Link>
                  ))}
                </div>
              </div>
              <div className="border-t border-stone p-5">
                {user
                  ? <Link href="/compte" onClick={() => setMenuOpen(false)} className="btn-secondary w-full">Mon espace client</Link>
                  : <Link href="/connexion" onClick={() => setMenuOpen(false)} className="btn-primary w-full">Se connecter</Link>}
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      <SearchOverlay open={searchOpen} onClose={() => setSearchOpen(false)} />
    </>
  );
}
