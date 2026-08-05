import type { NextConfig } from "next";

const securityHeaders = [
  // Prevents MIME-type sniffing
  { key: "X-Content-Type-Options", value: "nosniff" },
  // Disallows embedding in iframes
  { key: "X-Frame-Options", value: "DENY" },
  // Minimal referrer information to external origins
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  // Explicitly allow camera (required for PWA on some browsers)
  { key: "Permissions-Policy", value: "camera=(self)" },
];

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: securityHeaders,
      },
    ];
  },
};

export default nextConfig;
