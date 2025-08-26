#!/usr/bin/env python3
"""
Session Context Loader for Claude Code
Loads project index and recent changes at session start
"""
import json
import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

def get_recent_changes():
    """Get recent git changes if in a git repo."""
    try:
        # Check if we're in a git repo
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      capture_output=True, check=True)
        
        # Get recent commits
        result = subprocess.run(
            ['git', 'log', '--oneline', '-10', '--since=7.days.ago'],
            capture_output=True, text=True
        )
        recent_commits = result.stdout.strip()
        
        # Get current branch
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True, text=True
        )
        current_branch = result.stdout.strip()
        
        # Get uncommitted changes
        result = subprocess.run(
            ['git', 'status', '--short'],
            capture_output=True, text=True
        )
        uncommitted = result.stdout.strip()
        
        return {
            "branch": current_branch,
            "recent_commits": recent_commits.split('\n') if recent_commits else [],
            "uncommitted_files": len(uncommitted.split('\n')) if uncommitted else 0
        }
    except:
        return None

def load_project_context():
    """Load comprehensive project context."""
    project_root = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    context_parts = []
    
    # Load project index if it exists
    index_path = Path(project_root) / '.claude' / '.index.json'
    if index_path.exists():
        try:
            with open(index_path) as f:
                index = json.load(f)
            
            context_parts.append("## 📊 Project Index Summary")
            context_parts.append(f"- Total files: {index['stats']['total_files']}")
            context_parts.append(f"- Last indexed: {index['generated']}")
            
            # File types breakdown
            if index['stats']['by_type']:
                top_types = sorted(index['stats']['by_type'].items(), 
                                 key=lambda x: x[1], reverse=True)[:5]
                context_parts.append(f"- Main languages: {', '.join([f'{t[0]}({t[1]})' for t in top_types])}")
            
            # Critical files
            if index['critical_files']:
                context_parts.append("\n### 🔑 Critical Files:")
                for file in index['critical_files'][:10]:
                    context_parts.append(f"- {file}")
            
            # Entry points
            if index['entry_points']:
                context_parts.append("\n### 🚀 Entry Points:")
                for file in index['entry_points']:
                    context_parts.append(f"- {file}")
                    
        except Exception as e:
            pass
    
    # Add git context
    git_info = get_recent_changes()
    if git_info:
        context_parts.append("\n## 📝 Recent Git Activity")
        context_parts.append(f"- Current branch: {git_info['branch']}")
        context_parts.append(f"- Uncommitted changes: {git_info['uncommitted_files']} files")
        
        if git_info['recent_commits']:
            context_parts.append("- Recent commits:")
            for commit in git_info['recent_commits'][:5]:
                context_parts.append(f"  {commit}")
    
    # Load todo state if exists
    todo_path = Path(project_root) / '.claude' / '.todo_state.json'
    if todo_path.exists():
        try:
            with open(todo_path) as f:
                todos = json.load(f)
            
            pending = [t for t in todos if t['status'] == 'pending']
            if pending:
                context_parts.append("\n## 📋 Pending Tasks from Last Session")
                for todo in pending[:5]:
                    context_parts.append(f"- {todo['content']}")
        except:
            pass
    
    # Check for common build/test commands
    context_parts.append("\n## 🛠️ Available Commands")
    if (Path(project_root) / 'package.json').exists():
        try:
            with open(Path(project_root) / 'package.json') as f:
                pkg = json.load(f)
                if 'scripts' in pkg:
                    context_parts.append("NPM Scripts available:")
                    for script in list(pkg['scripts'].keys())[:8]:
                        context_parts.append(f"- npm run {script}")
        except:
            pass
    
    if (Path(project_root) / 'Makefile').exists():
        context_parts.append("Makefile targets available - use 'make' commands")
    
    if (Path(project_root) / 'Cargo.toml').exists():
        context_parts.append("Rust project - use 'cargo' commands")
    
    return '\n'.join(context_parts)

def main():
    try:
        input_data = json.load(sys.stdin)
        hook_event = input_data.get('hook_event_name', '')
        
        if hook_event == 'SessionStart':
            context = load_project_context()
            
            # Return as additional context
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context
                }
            }
            print(json.dumps(output))
        
    except Exception as e:
        sys.exit(1)

if __name__ == "__main__":
    main()