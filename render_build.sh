#!/bin/bash
# Render.com Build Script

echo "🔧 Building AI-Trader-Pro Backend..."

# Install dependencies
pip install -r backend/requirements.txt

# Create models directory
mkdir -p models

echo "✅ Build complete!"
