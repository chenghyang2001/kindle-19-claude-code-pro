import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // better-sqlite3 是原生模組，不能被打包進 server bundle
  serverExternalPackages: ["better-sqlite3"],
};

export default nextConfig;
