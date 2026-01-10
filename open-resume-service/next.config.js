/** @type {import('next').NextConfig} */
const nextConfig = {
  // Nextjs has an issue with pdfjs-dist which optionally uses the canvas package
  // for Node.js compatibility. This causes a "Module parse failed" error when
  // building the app. Since pdfjs-dist is only used on client side, we disable
  // the canvas package for webpack
  // https://github.com/mozilla/pdf.js/issues/16214
  output: 'standalone',
  webpack: (config, { isServer }) => {
    // Setting resolve.alias to false tells webpack to ignore a module
    // https://webpack.js.org/configuration/resolve/#resolvealias
    config.resolve.alias.canvas = false;
    config.resolve.alias.encoding = false;

    // Fix for @react-pdf/renderer: Ensure React is available with full API
    // The issue is that Next.js RSC strips React.Component from the bundle
    if (isServer) {
      // Add react and react-dom to externals for server-side code
      // This prevents webpack from bundling them and uses node_modules directly
      const externals = Array.isArray(config.externals)
        ? config.externals
        : config.externals
        ? [config.externals]
        : [];

      config.externals = [
        ...externals,
        {
          // Don't bundle React - use the actual node_modules version
          react: 'commonjs react',
          'react-dom': 'commonjs react-dom',
        },
      ];
    }

    return config;
  },
  experimental: {
    serverActions: true,
  },
};

module.exports = nextConfig;
