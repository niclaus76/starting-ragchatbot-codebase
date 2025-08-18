#!/bin/bash

# Code Quality Check Script
# Runs all quality checks and formatting tools

set -e

echo "🚀 Running Code Quality Checks"
echo "==============================="

# Navigate to project root
cd "$(dirname "$0")/.."

echo ""
echo "📦 Installing/updating dependencies..."
uv sync

echo ""
echo "🎨 Running code formatting..."
python scripts/format.py

echo ""
echo "🔍 Running code quality checks..."
python scripts/lint.py

echo ""
echo "✨ Quality check complete!"