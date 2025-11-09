#!/bin/bash

# Aevum Health Platform - Cleanup Script
# Removes unwanted files and cache directories

echo "🧹 Cleaning up Aevum Health Platform..."

# Remove Python cache files and directories
echo "Removing Python cache files..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Remove auto-generated schema files
echo "Removing auto-generated schema files..."
rm -f schema.json schema_new.json *.schema.json 2>/dev/null || true

# Remove temporary files
echo "Removing temporary files..."
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.temp" -delete 2>/dev/null || true
find . -name "*.cache" -delete 2>/dev/null || true
find . -name "*~" -delete 2>/dev/null || true
find . -name "*.swp" -delete 2>/dev/null || true
find . -name "*.swo" -delete 2>/dev/null || true

# Remove OS-specific files
echo "Removing OS-specific files..."
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "Thumbs.db" -delete 2>/dev/null || true

# Remove backup files
echo "Removing backup files..."
find . -name "*.bak" -delete 2>/dev/null || true
find . -name "*.orig" -delete 2>/dev/null || true

# Remove log files (optional - uncomment if needed)
# echo "Removing log files..."
# find . -name "*.log" -delete 2>/dev/null || true

# Remove test coverage files
echo "Removing test coverage files..."
rm -rf .coverage htmlcov/ .pytest_cache/ 2>/dev/null || true

# Remove Node modules if any
echo "Removing Node modules..."
rm -rf node_modules/ 2>/dev/null || true

echo "✅ Cleanup completed!"

# Show current directory size
echo "📊 Current project size:"
du -sh .

echo ""
echo "🎯 Files that remain ignored by .gitignore:"
echo "  - *.pyc, __pycache__/ (Python cache)"
echo "  - *.log (Log files)"
echo "  - schema*.json (Auto-generated API schemas)"
echo "  - *.tmp, *.temp, *.cache (Temporary files)"
echo "  - .DS_Store, Thumbs.db (OS files)"
echo "  - *.bak, *.orig (Backup files)"
echo "  - .env (Environment variables)"
echo "  - media/ (User uploads)"
echo ""
echo "🚀 Project is clean and ready!" 