import Link from "next/link";
import { redirect } from "next/navigation";
import type { ReactNode } from "react";
import { getCurrentUser } from "@/lib/auth";
import { logoutAction } from "@/actions/auth";
import { AccountNav } from "@/components/account/account-nav";
import { formatDate } from "@/lib/utils";
import { LogoutIcon, ExternalIcon } from "@/components/icons";

export default async function CompteLayout({ children }: { children: ReactNode }) {
  const user = await getCurrentUser();
  if (!user) redirect("/connexion?next=/compte");
  const staff = user.role === "admin" || user.role === "support";
  return (
    <div className="border-b border-stone">
      {/* Salon header */}
      <section className="bg-noir text-paper">
        <div className="container-lux flex flex-col gap-8 py-10 lg:flex-row lg:items-end lg:justify-between lg:py-12">
          <div>
            <p className="eyebrow mb-5 flex items-center gap-3 text-paper/55"><span className="font-display text-lg italic text-champagne-3">Votre espace</span> Client Cléopâtre</p>
            <h1 className="font-display text-display-lg">Bonjour <em className="text-champagne-3">{user.firstName}</em></h1>
            <p className="mt-3 text-sm text-paper/60">Cliente depuis le {formatDate(user.createdAt)} · {user.email}</p>
          </div>
          <div className="flex flex-wrap items-center gap-4">
            <span className="inline-flex items-center gap-2 border border-paper/25 px-4 py-2.5 text-xs text-paper/85"><span className="font-display text-lg italic text-champagne-3">{user.loyaltyPoints}</span> points fidélité</span>
            {staff && <Link href="/admin" className="inline-flex min-h-11 items-center gap-2 border border-champagne-3 px-4 text-[11px] font-bold uppercase tracking-[0.16em] text-champagne-3 transition-colors hover:bg-champagne-3 hover:text-noir"><ExternalIcon size={14} /> Administration</Link>}
            <form action={logoutAction}><button className="inline-flex min-h-11 items-center gap-2 px-3 text-[11px] font-bold uppercase tracking-[0.16em] text-paper/60 transition-colors hover:text-paper"><LogoutIcon size={14} /> Quitter</button></form>
          </div>
        </div>
      </section>

      <div className="container-lux grid gap-10 py-10 lg:grid-cols-12 lg:py-14">
        <AccountNav />
        <div className="min-w-0 lg:col-span-9">{children}</div>
      </div>
    </div>
  );
}
