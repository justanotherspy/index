#!/bin/bash

echo "🚀 Setting up Claude Code Enhanced Hook System"
echo "============================================="

# Create directories if needed
mkdir -p .claude/hooks
mkdir -p .claude/commands

# Make hooks executable
echo "✓ Making hooks executable..."
chmod +x .claude/hooks/*.py

# Run initial index
echo "✓ Building initial project index..."
python3 .claude/hooks/indexer.py

# Check if index was created
if [ -f ".claude/.index.json" ]; then
    echo "✓ Project index created successfully!"
    echo "  Files indexed: $(jq '.stats.total_files' .claude/.index.json)"
else
    echo "⚠ Index creation failed - check Python dependencies"
fi

# Add to gitignore if not already there
if [ -f ".gitignore" ]; then
    if ! grep -q ".claude/.index.json" .gitignore; then
        echo ".claude/.index.json" >> .gitignore
        echo ".claude/.todo_state.json" >> .gitignore
        echo ".claude/bash_history.log" >> .gitignore
        echo ".claude/settings.local.json" >> .gitignore
        echo "✓ Added Claude temp files to .gitignore"
    fi
fi

echo ""
echo "📋 Next Steps:"
echo "1. Restart Claude Code to load the hooks"
echo "2. Try: /readup - to analyze your project"
echo "3. Edit any file to see automatic indexing"
echo "4. Check .claude/.index.json for project structure"
echo ""
echo "✅ Setup complete! Enjoy enhanced Claude Code!"