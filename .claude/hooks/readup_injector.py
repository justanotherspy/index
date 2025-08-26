#!/usr/bin/env python3
"""
Readup Command Context Injector
Automatically loads project index when user asks for /readup or similar commands
"""
import json
import sys
import os
import re
from pathlib import Path

def should_inject_index(prompt):
    """Determine if we should inject the project index."""
    patterns = [
        r'/readup',
        r'understand.*project',
        r'explain.*codebase',
        r'what.*files.*here',
        r'project.*structure',
        r'how.*organized',
        r'architecture'
    ]
    
    prompt_lower = prompt.lower()
    return any(re.search(pattern, prompt_lower) for pattern in patterns)

def get_enhanced_context():
    """Get enhanced project context for deep understanding."""
    project_root = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    context_parts = []
    
    # Load full index
    index_path = Path(project_root) / '.claude' / '.index.json'
    if index_path.exists():
        try:
            with open(index_path) as f:
                index = json.load(f)
            
            context_parts.append("## 🗂️ Complete Project Structure Analysis\n")
            
            # Provide detailed breakdown
            context_parts.append("### File Organization:")
            context_parts.append(json.dumps(index['structure'], indent=2))
            
            context_parts.append("\n### Dependency Graph:")
            if index.get('dependencies_graph'):
                for file, deps in list(index['dependencies_graph'].items())[:20]:
                    if deps:
                        context_parts.append(f"- {file}: imports {', '.join(deps[:5])}")
            
            context_parts.append("\n### Statistics:")
            context_parts.append(f"- Total files: {index['stats']['total_files']}")
            for ftype, count in index['stats']['by_type'].items():
                context_parts.append(f"  - {ftype}: {count} files")
                
            # Add README content if exists
            readme_path = Path(project_root) / 'README.md'
            if readme_path.exists():
                try:
                    readme_content = readme_path.read_text()[:2000]
                    context_parts.append("\n### README Overview:")
                    context_parts.append(readme_content)
                except:
                    pass
                    
        except Exception as e:
            pass
    
    return '\n'.join(context_parts)

def main():
    try:
        input_data = json.load(sys.stdin)
        prompt = input_data.get('prompt', '')
        
        if should_inject_index(prompt):
            context = get_enhanced_context()
            
            # Return additional context
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": f"[Automatic Project Context Loaded]\n{context}"
                }
            }
            print(json.dumps(output))
        
        sys.exit(0)
        
    except Exception as e:
        sys.exit(1)

if __name__ == "__main__":
    main()