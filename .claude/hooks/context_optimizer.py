#!/usr/bin/env python3
"""
Context Optimizer for PreCompact
Preserves critical context before Claude compacts the conversation
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime

def extract_critical_context():
    """Extract critical context to preserve during compaction."""
    context_parts = []
    project_root = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    
    # Load current index summary
    index_path = Path(project_root) / '.claude' / '.index.json'
    if index_path.exists():
        with open(index_path) as f:
            index = json.load(f)
            
        context_parts.append("## Project Context to Preserve:")
        context_parts.append(f"- Project has {index['stats']['total_files']} files")
        context_parts.append(f"- Critical files: {', '.join(index['critical_files'][:5])}")
        
        # Add entry points if any
        if index['entry_points']:
            context_parts.append(f"- Entry points: {', '.join(index['entry_points'])}")
    
    # Check for recent work patterns
    bash_log = Path(project_root) / '.claude' / 'bash_history.log'
    if bash_log.exists():
        try:
            with open(bash_log) as f:
                lines = f.readlines()
                if lines:
                    recent_commands = lines[-10:]  # Last 10 commands
                    context_parts.append("\n## Recent Commands Used:")
                    for cmd in recent_commands[-5:]:  # Show last 5
                        context_parts.append(f"- {cmd.strip()}")
        except:
            pass
    
    # Load current todos if any
    todo_path = Path(project_root) / '.claude' / '.todo_state.json'
    if todo_path.exists():
        try:
            with open(todo_path) as f:
                state = json.load(f)
                todos = state.get('todos', [])
                pending = [t for t in todos if t.get('status') == 'pending']
                if pending:
                    context_parts.append("\n## Current Tasks:")
                    for todo in pending[:5]:
                        context_parts.append(f"- {todo['content']}")
        except:
            pass
    
    return '\n'.join(context_parts)

def main():
    try:
        input_data = json.load(sys.stdin)
        hook_event = input_data.get('hook_event_name', '')
        
        if hook_event == 'PreCompact':
            context = extract_critical_context()
            
            # Save context to be included after compaction
            project_root = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
            context_file = Path(project_root) / '.claude' / '.preserved_context.md'
            
            with open(context_file, 'w') as f:
                f.write(f"# Context Preserved from {datetime.now().isoformat()}\n\n")
                f.write(context)
            
            print(f"💾 Preserved critical context before compaction")
            
    except Exception as e:
        pass
    
    sys.exit(0)

if __name__ == "__main__":
    main()