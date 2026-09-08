import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { getCurrentUser } from "@/lib/auth";
import { LoginForm } from "@/components/account/auth-forms";
import { AuthShell } from "@/components/account/auth-shell";
export const metadata: Metadata = { title: "Connexion", robots: { index: false } };
export default async function ConnexionPage({ searchParams }: { searchParams: Promise<{ next?: string }> }) {
  const { next } = await searchParams;
  if (await getCurrentUser()) redirect(next && next.startsWith("/") ? next : "/compte");
  return (
    <AuthShell kicker="Retrouver votre espace" title={<>Bon retour <em className="text-champagne-2">parmi nous</em></>}>
      <LoginForm next={next} />
    </AuthShell>
  );
}
