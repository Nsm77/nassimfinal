import { desc, eq } from "drizzle-orm";
import { redirect } from "next/navigation";
import { db } from "@/db";
import { addresses } from "@/db/schema";
import { getCurrentUser } from "@/lib/auth";
import { AddressList, PasswordForm, ProfileForm } from "@/components/account/profile-forms";
export const dynamic = "force-dynamic";
export default async function ProfilPage() {
  // Do not rely on the layout having redirected: Next.js renders the page
  // alongside it, so an anonymous request would otherwise dereference null.
  const user = await getCurrentUser();
  if (!user) redirect("/connexion?next=/compte/profil");
  const list = await db.select().from(addresses).where(eq(addresses.userId, user.id)).orderBy(desc(addresses.isDefault));
  return (
    <div className="space-y-14">
      <section><h2 className="mb-6 font-display text-display-sm text-ink">Informations</h2><ProfileForm user={user} /></section>
      <section><h2 className="mb-6 font-display text-display-sm text-ink">Adresses</h2><AddressList addresses={list} /></section>
      <section><h2 className="mb-6 font-display text-display-sm text-ink">Mot de passe</h2><PasswordForm /></section>
    </div>
  );
}
