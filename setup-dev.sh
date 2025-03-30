#!/bin/bash

set -e

echo "🔧 Installing Python dependencies..."
pip install -e .

echo "📁 Installing Node.js dependencies for puppeteer_scraper.js..."
cd scrapedocs
npm install

echo "✅ Setup complete! You can now use 'spa-scrape' and 'scrape-docs'."