#!/bin/bash
# Production build script

echo "🏗️  Building Aetherra Website for Production..."
echo "📁 Source: website-src/"
echo "🌐 Output: docs/"
echo ""

cd website-src
npm install
npm run build

echo ""
echo "✅ Build complete!"
echo "📂 Files generated in docs/ directory"
echo "🚀 Ready for GitHub Pages deployment"
echo "🌍 Live at: https://aetherra.dev"
