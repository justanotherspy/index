#!/usr/bin/env python3
"""
Smart Git Committer
Automatically stages and suggests commit messages based on changes
"""
import json
import sys
import subprocess
import re
from pathlib import Path

def analyze_changes():
    """Analyze git changes and suggest commit message."""
    try:
        # Get diff
        result = subprocess.run(['git', 'diff', '--staged', '--stat'],
                              capture_output=True, text=True)
        if not result.stdout:
            # No staged changes, check unstaged
            result = subprocess.run(['git', 'diff', '--stat'],
                                  capture_output=True, text=True)
        
        if not result.stdout:
            return None
            
        changes = result.stdout
        
        # Analyze changes for commit message
        suggestions = []
        
        if 'package.json' in changes:
            suggestions.append("📦 Update dependencies")
        if re.search(r'test.*\.(js|py|rs)', changes):
            suggestions.append("✅ Update tests")
        if re.search(r'\.(md|txt|rst)(\s|$)', changes):
            suggestions.append("📝 Update documentation")
        if 'feat' in changes or 'feature' in changes:
            suggestions.append("✨ Add new feature")
        if 'fix' in changes or 'bug' in changes:
            suggestions.append("🐛 Fix bug")
        if re.search(r'\.css|\.scss|style', changes):
            suggestions.append("💄 Update styles")
        if 'refactor' in changes:
            suggestions.append("♻️ Refactor code")
        
        return suggestions[0] if suggestions else "🔧 Update code"
        
    except:
        return None

def main():
    try:
        input_data = json.load(sys.stdin)
        hook_event = input_data.get('hook_event_name', '')
        
        if hook_event == 'Stop':
            # Check for uncommitted changes
            result = subprocess.run(['git', 'status', '--porcelain'],
                                  capture_output=True, text=True)
            
            if result.stdout:
                suggestion = analyze_changes()
                if suggestion:
                    output = {
                        "decision": "block",
                        "reason": f"You have uncommitted changes. Suggested commit: '{suggestion}'. Would you like me to commit them?"
                    }
                    print(json.dumps(output))
                    
    except:
        pass
    
    sys.exit(0)

if __name__ == "__main__":
    main()