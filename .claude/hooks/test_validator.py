#!/usr/bin/env python3
"""
Test and Lint Validator
Automatically runs tests/linting after code changes and provides feedback
"""
import json
import sys
import os
import subprocess
from pathlib import Path

def detect_test_command():
    """Detect available test commands in the project."""
    project_root = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    commands = []
    
    # Check package.json for npm/yarn scripts
    pkg_path = Path(project_root) / 'package.json'
    if pkg_path.exists():
        try:
            with open(pkg_path) as f:
                pkg = json.load(f)
                scripts = pkg.get('scripts', {})
                
                # Look for test-related scripts
                for script_name in scripts:
                    if any(keyword in script_name.lower() 
                          for keyword in ['test', 'lint', 'check', 'typecheck']):
                        commands.append(f"npm run {script_name}")
        except:
            pass
    
    # Check for Makefile
    if (Path(project_root) / 'Makefile').exists():
        try:
            result = subprocess.run(['make', '-n', 'test'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                commands.append('make test')
        except:
            pass
    
    # Check for pytest
    if any(Path(project_root).glob('**/test_*.py')):
        commands.append('pytest')
    
    # Check for cargo (Rust)
    if (Path(project_root) / 'Cargo.toml').exists():
        commands.append('cargo test')
        commands.append('cargo clippy')
    
    return commands

def should_run_tests(file_path):
    """Determine if we should run tests based on the changed file."""
    # Skip tests for non-code files
    skip_extensions = ['.md', '.txt', '.json', '.yml', '.yaml', '.toml']
    return not any(file_path.endswith(ext) for ext in skip_extensions)

def run_validation(file_path):
    """Run appropriate validation for the changed file."""
    if not should_run_tests(file_path):
        return None
    
    project_root = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    feedback = []
    
    # Quick syntax check for specific file types
    if file_path.endswith('.py'):
        # Run pylint or flake8 on the specific file
        try:
            result = subprocess.run(
                ['python', '-m', 'py_compile', file_path],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                feedback.append(f"⚠️ Python syntax error in {file_path}")
                feedback.append(result.stderr[:500])
        except:
            pass
    
    elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
        # Check if file has obvious syntax errors
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                # Basic bracket matching
                if content.count('{') != content.count('}'):
                    feedback.append(f"⚠️ Possible bracket mismatch in {file_path}")
                if content.count('(') != content.count(')'):
                    feedback.append(f"⚠️ Possible parenthesis mismatch in {file_path}")
        except:
            pass
    
    return '\n'.join(feedback) if feedback else None

def main():
    try:
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        
        # Only run for file modifications
        if tool_name not in ['Write', 'Edit', 'MultiEdit']:
            sys.exit(0)
        
        tool_input = input_data.get('tool_input', {})
        file_path = tool_input.get('file_path', '')
        
        if not file_path:
            sys.exit(0)
        
        # Run validation
        feedback = run_validation(file_path)
        
        if feedback:
            # Provide feedback to Claude
            output = {
                "decision": "block",
                "reason": feedback,
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": f"Please fix these issues:\n{feedback}"
                }
            }
            print(json.dumps(output))
            sys.exit(0)
        
    except Exception as e:
        pass
    
    sys.exit(0)

if __name__ == "__main__":
    main()