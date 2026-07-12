#!/bin/bash
set -e
echo "🚀 Building Jay Chou Music Analysis website..."
npm install
npx vite build
echo ""
echo "✅ Build complete! Output in dist/"
echo ""
echo "To deploy:"
echo "  Vercel:    cd website && vercel --prod"
echo "  GitHub:    cd website && npx gh-pages -d dist"
echo "  OR simply: open dist/index.html"
