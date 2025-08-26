#!/usr/bin/env python3
"""
Todo State Persister
Saves todo state between sessions for continuity
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime

def save_todo_state():
    """Extract and save current todo state from transcript."""
    try:
        input_data = json.load(sys.stdin)
        transcript_path = input_data.get('transcript_path', '')
        
        if not transcript_path or not os.path.exists(transcript_path):
            return
        
        # Read the transcript
        with open(transcript_path, 'r') as f:
            todos = []
            for line in f:
                try:
                    entry = json.loads(line)
                    # Look for TodoWrite tool usage
                    if (entry.get('type') == 'tool_use' and 
                        entry.get('name') == 'TodoWrite'):
                        todos_data = entry.get('input', {}).get('todos', [])
                        if todos_data:
                            todos = todos_data  # Keep the latest todo state
                except:
                    continue
        
        if todos:
            # Save to project directory
            project_root = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
            todo_path = Path(project_root) / '.claude' / '.todo_state.json'
            todo_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Add metadata
            state = {
                "saved_at": datetime.now().isoformat(),
                "session_id": input_data.get('session_id', ''),
                "todos": todos
            }
            
            with open(todo_path, 'w') as f:
                json.dump(state, f, indent=2)
            
            # Count pending tasks
            pending_count = len([t for t in todos if t.get('status') == 'pending'])
            if pending_count > 0:
                print(f"💾 Saved {pending_count} pending tasks for next session")
        
    except Exception as e:
        pass

def main():
    save_todo_state()
    sys.exit(0)

if __name__ == "__main__":
    main()