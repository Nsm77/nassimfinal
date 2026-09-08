import type { MetadataRoute } from "next";
import { eq } from "drizzle-orm";
import { db } from "@/db";
import { articles, brands, categories, concerns, products } from "@/db/schema";
import { SITE_URL } from "@/lib/env";

export const dynamic = "force-dynamic";
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [p, c, b, k, a] = await Promise.all([
    db.select({ slug: products.slug, u: products.updatedAt }).from(products).where(eq(products.status, "active")),
    db.select({ slug: categories.slug, isUniverse: categories.isUniverse, u: categories.updatedAt }).from(categories),
    db.select({ slug: brands.slug, u: brands.updatedAt }).from(brands),
    db.select({ slug: concerns.slug, u: concerns.updatedAt }).from(concerns),
    db.select({ slug: articles.slug, u: articles.updatedAt }).from(articles).where(eq(articles.isPublished, true)),
  ]);
  const statics = ["", "/boutique", "/marques", "/promotions", "/journal", "/boutiques", "/aide", "/livraison", "/cgv", "/confidentialite"].map((path) => ({ url: `${SITE_URL}${path}`, changeFrequency: "weekly" as const, priority: path === "" ? 1 : 0.6 }));
  return [
    ...statics,
    ...p.map((x) => ({ url: `${SITE_URL}/produit/${x.slug}`, lastModified: x.u, changeFrequency: "weekly" as const, priority: 0.8 })),
    ...c.map((x) => ({ url: `${SITE_URL}/${x.isUniverse ? "univers" : "categorie"}/${x.slug}`, lastModified: x.u, changeFrequency: "weekly" as const, priority: 0.7 })),
    ...b.map((x) => ({ url: `${SITE_URL}/marque/${x.slug}`, lastModified: x.u, changeFrequency: "monthly" as const, priority: 0.5 })),
    ...k.map((x) => ({ url: `${SITE_URL}/besoin/${x.slug}`, lastModified: x.u, changeFrequency: "monthly" as const, priority: 0.5 })),
    ...a.map((x) => ({ url: `${SITE_URL}/journal/${x.slug}`, lastModified: x.u, changeFrequency: "monthly" as const, priority: 0.5 })),
  ];
}
