import Image from "next/image";
import type { ReactNode } from "react";
import { Breadcrumbs } from "@/components/ui/primitives";
import { cn } from "@/lib/utils";

/* ── Editorial page masthead ─────────────────────────────────────
   Used by inner pages so each destination opens like a chapter:
   breadcrumb · numbered kicker · oversized display title · intro.
   Variants give each page its own rhythm. */
export function PageIntro({
  kicker, index, title, intro, breadcrumbs, image, imageAlt, imagePriority = false, right, children, className, tone = "paper",
}: {
  kicker?: string; index?: string; title: ReactNode; intro?: ReactNode;
  breadcrumbs?: { href?: string; label: string }[];
  image?: string | null; imageAlt?: string; imagePriority?: boolean;
  right?: ReactNode; children?: ReactNode; className?: string; tone?: "paper" | "cream" | "noir";
}) {
  const dark = tone === "noir";
  return (
    <section className={cn(dark ? "bg-noir text-paper" : tone === "cream" ? "bg-cream" : "border-b border-stone", dark && "border-b border-paper/10")}>
      <div className={cn("container-lux", className ?? "py-10 lg:py-16")}>
        {breadcrumbs && <div className="mb-10"><Breadcrumbs items={breadcrumbs} light={dark} /></div>}
        <div className="grid items-end gap-10 lg:grid-cols-12">
          <div className={cn("max-w-3xl", image || right ? "lg:col-span-7" : "lg:col-span-9")}>
            {(kicker || index) && (
              <p className={cn("eyebrow mb-6 flex items-center gap-3", dark && "text-paper/60")}>
                {index && <span className={cn("font-display text-lg italic", dark ? "text-champagne-3" : "text-champagne-2")}>{index}</span>}
                {kicker}
              </p>
            )}
            <h1 className={cn("font-display text-display-lg", dark ? "text-paper" : "text-ink")}>{title}</h1>
            {intro && <p className={cn("mt-6 max-w-xl text-[15px] leading-relaxed", dark ? "text-paper/70" : "text-muted")}>{intro}</p>}
            {right && <div className="mt-9 flex flex-wrap items-center gap-4">{right}</div>}
          </div>
          {image && (
            <div className={cn("frame aspect-[4/3] w-full lg:col-span-5 lg:aspect-[5/4]", dark && "border border-paper/10")}>
              <Image src={image} alt={imageAlt ?? ""} fill priority={imagePriority} sizes="(max-width:1024px) 100vw, 40vw" className="object-cover" />
            </div>
          )}
        </div>
        {children}
      </div>
    </section>
  );
}
