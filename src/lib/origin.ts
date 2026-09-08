import { headers } from "next/headers";
import { env, IS_PRODUCTION, SITE_URL } from "./env";

/**
 * Defence-in-depth origin check for state-changing Server Actions.
 *
 * Next.js already rejects cross-origin Server Action POSTs by comparing Origin
 * with the request host; this widens that check so it also works behind a
 * reverse proxy and against the canonical site URL, without rejecting
 * legitimate traffic:
 *   • `host` — direct requests.
 *   • `x-forwarded-host` — the public host when running behind a proxy/CDN.
 *   • the configured `NEXT_PUBLIC_SITE_URL` — canonical deployment origin.
 *
 * A missing Origin is allowed: browsers always send Origin on cross-origin
 * POSTs, so its absence indicates a same-origin or non-browser navigation,
 * which Next.js's own check already covers.
 */
export async function checkOrigin(): Promise<boolean> {
  const h = await headers();
  const origin = h.get("origin");
  if (!origin) return true;

  let originHost: string;
  try {
    originHost = new URL(origin).host;
  } catch {
    return false;
  }

  const allowed = new Set<string>();
  for (const raw of [h.get("host"), h.get("x-forwarded-host")]) {
    // x-forwarded-host can carry a comma-separated chain; trust the first entry.
    const first = raw?.split(",")[0]?.trim();
    if (first) allowed.add(first.toLowerCase());
  }
  try {
    allowed.add(new URL(SITE_URL).host.toLowerCase());
  } catch {
    /* ignore a malformed configured URL */
  }
  if (!IS_PRODUCTION) allowed.add("localhost:3000");

  return allowed.has(originHost.toLowerCase());
}

/**
 * Stable per-client key for the rate limiter.
 *
 * Forwarded headers are only honoured when `TRUST_PROXY` is set, and then read
 * from the RIGHT of the `x-forwarded-for` chain: every proxy appends the address
 * it received the request from, so the left-most entries are client-supplied and
 * trivially spoofable. Counting back `TRUST_PROXY_HOPS` entries lands on the
 * address our own proxy recorded.
 *
 * Untrusted, every caller collapses to `"local"` — one shared bucket. That is a
 * deliberate trade: a global limiter degrades availability, whereas trusting the
 * header silently hands out unlimited attempts to anyone who sets it.
 */
export async function clientKey(): Promise<string> {
  const h = await headers();
  if (!env.TRUST_PROXY) return "local";

  const chain = (h.get("x-forwarded-for") ?? "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  if (chain.length) {
    const idx = Math.max(0, chain.length - env.TRUST_PROXY_HOPS);
    return chain[idx];
  }
  return h.get("x-real-ip")?.trim() || "local";
}
