#!/usr/bin/env python3
"""
Automatic Project Indexer for Claude Code
Updates .claude/.index.json with file structure and dependencies
"""
import json
import sys
import os
import re
import hashlib
from pathlib import Path
from datetime import datetime

def get_file_info(file_path):
    """Extract metadata and dependencies from a file."""
    info = {
        "path": str(file_path),
        "type": file_path.suffix[1:] if file_path.suffix else "none",
        "size": file_path.stat().st_size,
        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
        "dependencies": [],
        "exports": [],
        "purpose": "",
        "importance": "normal"
    }
    
    if not file_path.is_file() or file_path.stat().st_size > 100000:
        return info
        
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        
        # JavaScript/TypeScript analysis
        if file_path.suffix in ['.js', '.ts', '.jsx', '.tsx']:
            # Find imports
            imports = re.findall(r"(?:import|require)\s*\(?['\"]([^'\"]+)['\"]", content)
            info["dependencies"] = list(set(imports))
            
            # Find exports
            exports = re.findall(r"export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)", content)
            info["exports"] = list(set(exports))
            
            # Detect purpose
            if re.search(r"(test|spec)\.(js|ts)x?$", str(file_path)):
                info["purpose"] = "test"
                info["importance"] = "low"
            elif "index" in file_path.name:
                info["purpose"] = "entry_point"
                info["importance"] = "high"
            elif re.search(r"(config|setup)", file_path.name, re.I):
                info["purpose"] = "configuration"
                info["importance"] = "high"
                
        # Python analysis
        elif file_path.suffix == '.py':
            imports = re.findall(r"^(?:from\s+(\S+)|import\s+(\S+))", content, re.M)
            info["dependencies"] = list(set([i[0] or i[1] for i in imports]))
            
            # Find class/function definitions
            defs = re.findall(r"^(?:class|def)\s+(\w+)", content, re.M)
            info["exports"] = list(set(defs))
            
            if "__main__" in content:
                info["purpose"] = "script"
                info["importance"] = "high"
            elif "test_" in file_path.name or "_test" in file_path.name:
                info["purpose"] = "test"
                info["importance"] = "low"
                
        # Rust analysis
        elif file_path.suffix == '.rs':
            uses = re.findall(r"use\s+([^;]+);", content)
            info["dependencies"] = list(set(uses))
            
            if file_path.name == "main.rs":
                info["purpose"] = "entry_point"
                info["importance"] = "high"
            elif file_path.name == "lib.rs":
                info["purpose"] = "library"
                info["importance"] = "high"
                
        # Configuration files
        elif file_path.name in ['package.json', 'Cargo.toml', 'pyproject.toml', 
                               'docker-compose.yml', '.env.example']:
            info["purpose"] = "configuration"
            info["importance"] = "critical"
            
        # Documentation
        elif file_path.suffix in ['.md', '.mdx']:
            if file_path.name.upper() == 'README.MD':
                info["purpose"] = "documentation"
                info["importance"] = "critical"
            else:
                info["purpose"] = "documentation"
                info["importance"] = "normal"
                
    except Exception as e:
        pass
        
    return info

def build_project_index(root_path):
    """Build comprehensive project index."""
    index = {
        "version": "1.0",
        "generated": datetime.now().isoformat(),
        "root": str(root_path),
        "stats": {
            "total_files": 0,
            "by_type": {},
            "by_purpose": {}
        },
        "structure": {},
        "critical_files": [],
        "entry_points": [],
        "test_files": [],
        "dependencies_graph": {}
    }
    
    # Patterns to ignore
    ignore_patterns = [
        '.git', 'node_modules', '__pycache__', '.pytest_cache',
        'dist', 'build', 'target', '.next', '.venv', 'env'
    ]
    
    files_data = {}
    
    for file_path in Path(root_path).rglob('*'):
        # Skip ignored directories
        if any(pattern in str(file_path) for pattern in ignore_patterns):
            continue
            
        if file_path.is_file():
            rel_path = file_path.relative_to(root_path)
            info = get_file_info(file_path)
            files_data[str(rel_path)] = info
            
            # Update stats
            index["stats"]["total_files"] += 1
            file_type = info["type"]
            index["stats"]["by_type"][file_type] = index["stats"]["by_type"].get(file_type, 0) + 1
            
            if info["purpose"]:
                purpose = info["purpose"]
                index["stats"]["by_purpose"][purpose] = index["stats"]["by_purpose"].get(purpose, 0) + 1
                
                # Categorize special files
                if info["importance"] in ["critical", "high"]:
                    index["critical_files"].append(str(rel_path))
                if info["purpose"] == "entry_point":
                    index["entry_points"].append(str(rel_path))
                elif info["purpose"] == "test":
                    index["test_files"].append(str(rel_path))
    
    # Build directory structure
    for file_path, info in files_data.items():
        parts = file_path.split('/')
        current = index["structure"]
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = {
            "type": info["type"],
            "purpose": info["purpose"],
            "importance": info["importance"]
        }
    
    # Build dependency graph (simplified)
    for file_path, info in files_data.items():
        if info["dependencies"]:
            index["dependencies_graph"][file_path] = info["dependencies"]
    
    return index

def main():
    # Check if stdin has data (when called as a hook)
    if not sys.stdin.isatty():
        try:
            input_data = json.load(sys.stdin)
            # Check if this is a relevant file change
            tool_name = input_data.get('tool_name', '')
            if tool_name not in ['Write', 'Edit', 'MultiEdit']:
                sys.exit(0)
        except:
            # If no valid JSON, assume manual run
            pass
    
    # Get project root
    project_root = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    
    # Build and save index
    index = build_project_index(project_root)
    
    index_path = Path(project_root) / '.claude' / '.index.json'
    index_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)
        
    print(f"✓ Updated project index: {index['stats']['total_files']} files indexed")
        
if __name__ == "__main__":
    main()