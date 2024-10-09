/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['pdfjs-dist'],
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        stream: false,
        path: false,
      };
    }
    config.module.rules.push({
      test: /pdf\.worker\.min\.mjs$/,
      type: 'asset/resource',
      generator: {
        filename: 'static/chunks/[name].[hash][ext]',
      },
    });
    return config;
  },
};

module.exports = nextConfig;