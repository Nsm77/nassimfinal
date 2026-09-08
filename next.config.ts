import type { NextConfig } from "next";

const securityHeaders = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
  { key: "X-DNS-Prefetch-Control", value: "on" },
];

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  /*
   * The live preview is served through a dynamic proxy host such as
   * `3000-<sandbox>.e2b.app`. In development Next.js refuses to serve its own
   * dev resources (the `/_next/static` JS chunks, the HMR websocket) to a
   * cross-origin host unless it is allow-listed here. Without this the preview
   * receives the server-rendered HTML but none of the client scripts run, so
   * scroll-reveal sections are stuck at `opacity: 0` and the page looks empty.
   * Dev-only: `allowedDevOrigins` has no effect in a production build.
   */
  allowedDevOrigins: ["*.e2b.app"],
  images: {
    formats: ["image/avif", "image/webp"],
    remotePatterns: [{ protocol: "https", hostname: "images.unsplash.com" }],
  },
  async headers() {
    return [{ source: "/(.*)", headers: securityHeaders }];
  },
};

export default nextConfig;
