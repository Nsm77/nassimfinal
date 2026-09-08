import Link from "next/link";
import { redirect } from "next/navigation";
import type { ReactNode } from "react";
import type { Metadata } from "next";
import { getCurrentUser } from "@/lib/auth";
import { logoutAction } from "@/actions/auth";
import { AdminNav } from "@/components/admin/admin-nav";
import { ExternalIcon, LogoMark, LogoutIcon } from "@/components/icons";
export const metadata: Metadata = { title: { default: "Administration", template: "%s — Admin Cléopâtre" }, robots: { index: false, follow: false } };
export default async function AdminLayout({ children }: { children: ReactNode }) {
  const user = await getCurrentUser();
  if (!user) redirect("/connexion?next=/admin");
  if (user.role !== "admin" && user.role !== "support") redirect("/compte");
  return (
    <div className="min-h-dvh bg-admin-bg text-admin-text">
      {/* Top bar */}
      <header className="sticky top-0 z-40 border-b border-admin-border bg-admin-bg/95 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-[110rem] items-center justify-between gap-4 px-4 lg:px-8">
          <Link href="/admin" className="group flex items-center gap-3">
            <LogoMark size={26} className="text-admin-gold" />
            <span className="flex flex-col leading-none">
              <span className="font-display text-[19px] tracking-[0.01em]">Cléopâtre</span>
              <span className="mt-0.5 text-[8px] font-bold uppercase tracking-[0.3em] text-admin-muted">Back office</span>
            </span>
          </Link>
          <div className="flex items-center gap-6 text-xs">
            <span className="hidden items-center gap-2 md:flex">
              <span className="flex h-7 w-7 items-center justify-center rounded-full border border-admin-border bg-admin-panel font-display text-xs italic text-admin-gold">{user.firstName.charAt(0)}{user.lastName.charAt(0)}</span>
              <span className="flex flex-col leading-tight">
                <span className="text-admin-text">{user.firstName} {user.lastName}</span>
                <span className="text-[10px] uppercase tracking-[0.18em] text-admin-muted">{user.role === "admin" ? "Administrateur" : "Support"}</span>
              </span>
            </span>
            <Link href="/" className="flex min-h-10 items-center gap-1.5 text-admin-muted transition-colors hover:text-admin-gold"><ExternalIcon size={13} /> <span className="hidden sm:inline">Voir la boutique</span></Link>
            <form action={logoutAction}><button className="flex min-h-10 items-center gap-1.5 text-admin-muted transition-colors hover:text-admin-gold"><LogoutIcon size={13} /> <span className="hidden sm:inline">Quitter</span></button></form>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-[110rem] gap-8 px-4 py-6 lg:grid-cols-[236px_1fr] lg:px-8 lg:py-8">
        <aside className="lg:border-r lg:border-admin-border lg:pr-6">
          <div className="lg:sticky lg:top-24"><AdminNav role={user.role} /></div>
        </aside>
        <main className="min-w-0">{children}</main>
      </div>
    </div>
  );
}
