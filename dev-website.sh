#!/bin/bash
# Development server start script

echo "🚀 Starting Aetherra Website Development Server..."
echo "📁 Source: website-src/"
echo "🌐 Output: docs/"
echo "🔗 Live at: http://localhost:3000"
echo ""

cd website-src
npm install
npm run dev
