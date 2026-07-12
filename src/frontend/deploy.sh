#!/bin/bash
set -e
echo "🚀 Building Jay Chou Music Analysis website..."
npm install
npx vite build
echo ""
echo "✅ Build complete! Output in dist/"
echo ""
echo "To deploy:"
echo "  Vercel:    cd src/frontend && vercel --prod"
echo "  GitHub:    cd src/frontend && npx gh-pages -d dist"
echo "  OR simply: open dist/index.html"
