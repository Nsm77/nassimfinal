import { z } from "zod";

/**
 * Values that must never be accepted in production. A `.default()` on a secret
 * is how a demo credential quietly becomes the live one: the app boots happily
 * and nobody notices. In production these are hard failures at startup instead.
 */
const INSECURE_SECRETS = new Set([
  "cleopatre-dev-secret-change-me-please",
  "change-me-to-a-long-random-string",
  "changeme",
  "secret",
]);

const schema = z.object({
  DATABASE_URL: z.string().url(),
  // No default on purpose — see the production check below.
  SESSION_SECRET: z.string().min(16).optional(),
  NEXT_PUBLIC_SITE_URL: z.string().url().default("http://localhost:3000"),
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  /*
   * `x-forwarded-for` / `x-real-ip` are only meaningful when a reverse proxy we
   * control sets them. Left untrusted, an attacker rotates the header and gets a
   * fresh rate-limit bucket on every request, which defeats every limiter in the
   * app (login brute-force included). Off by default so the safe behaviour is the
   * default one; see README.
   */
  TRUST_PROXY: z
    .enum(["true", "false"])
    .default("false")
    .transform((v) => v === "true"),
  // How many proxies between the client and the app append to x-forwarded-for.
  // Counting back from the right skips the client-supplied (spoofable) entries.
  TRUST_PROXY_HOPS: z.coerce.number().int().min(1).max(10).default(1),
});

const parsed = schema.parse({
  DATABASE_URL: process.env.DATABASE_URL,
  SESSION_SECRET: process.env.SESSION_SECRET,
  NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL,
  NODE_ENV: process.env.NODE_ENV,
  TRUST_PROXY: process.env.TRUST_PROXY,
  TRUST_PROXY_HOPS: process.env.TRUST_PROXY_HOPS,
});

const isProduction = parsed.NODE_ENV === "production";

if (isProduction) {
  const problems: string[] = [];
  if (!parsed.SESSION_SECRET) {
    problems.push("SESSION_SECRET is required in production (32+ random bytes).");
  } else if (parsed.SESSION_SECRET.length < 32) {
    problems.push("SESSION_SECRET must be at least 32 characters in production.");
  } else if (INSECURE_SECRETS.has(parsed.SESSION_SECRET)) {
    problems.push("SESSION_SECRET is a known placeholder value; generate a real one.");
  }
  if (problems.length) {
    // Fail loudly at boot rather than serving traffic with a guessable secret.
    throw new Error(`Refusing to start with unsafe production configuration:\n- ${problems.join("\n- ")}`);
  }
  if (!parsed.TRUST_PROXY) {
    // Not fatal, but the operator needs to know: without it every visitor shares
    // one rate-limit bucket, so a busy site will throttle legitimate users.
    console.warn(
      "[env] TRUST_PROXY is not set. Rate limiting is keyed to a single shared " +
        'client, which will throttle real users. Set TRUST_PROXY=true if the app ' +
        "runs behind a reverse proxy that sets x-forwarded-for.",
    );
  }
}

export const env = {
  ...parsed,
  // Development keeps a stable, obviously-fake value so local setup stays easy;
  // production has already been proven to carry a real one.
  SESSION_SECRET: parsed.SESSION_SECRET ?? "cleopatre-dev-secret-change-me-please",
} as const;

export const SITE_URL = env.NEXT_PUBLIC_SITE_URL;
export const SITE_NAME = "Cléopâtre — Espace Santé Beauté";
export const IS_PRODUCTION = isProduction;
