#!/usr/bin/env python3
"""
Manual Project Indexer - Run this to build initial index
"""
import sys
import os
# Add parent directory to path to import indexer module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the indexer functions
from indexer import build_project_index
import json
from pathlib import Path

def main():
    project_root = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    print(f"Building index for: {project_root}")
    
    # Build index
    index = build_project_index(project_root)
    
    # Save index
    index_path = Path(project_root) / '.claude' / '.index.json'
    index_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)
    
    # Print summary
    print(f"✓ Index created: {index_path}")
    print(f"  Total files: {index['stats']['total_files']}")
    print(f"  File types: {', '.join(index['stats']['by_type'].keys())}")
    print(f"  Critical files: {len(index['critical_files'])}")
    print(f"  Entry points: {len(index['entry_points'])}")

if __name__ == "__main__":
    main()