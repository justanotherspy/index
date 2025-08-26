# 🚀 Claude Code Enhanced Hook System

A comprehensive hook system that gives Claude Code better context and tools for optimal output quality.

## 📋 What This System Does

### 1. **Automatic Project Indexing** 
- Creates and maintains `.claude/.index.json` with complete project structure
- Tracks dependencies, exports, and file relationships
- Identifies critical files, entry points, and test files
- Updates automatically when you edit files

### 2. **Session Context Loading**
- Loads project index at session start
- Shows recent git activity and current branch
- Restores pending todos from previous session
- Identifies available build/test commands

### 3. **Smart Command Enhancement**
- `/readup` command for deep project analysis
- Automatic context injection when you ask about the project
- Pattern matching for architecture/structure questions

### 4. **Continuous Validation**
- Runs syntax checks after file edits
- Detects common issues (bracket mismatches, syntax errors)
- Provides immediate feedback to fix issues

### 5. **Git Workflow Assistance**
- Tracks all bash commands for audit
- Suggests commit messages based on changes
- Reminds about uncommitted changes

## 🔧 Installation

### One-Line Installation (Recommended)
```bash
curl -sSL https://github.com/YOUR_USERNAME/YOUR_REPO/raw/main/install.sh | bash
```

### Alternative Installation Methods

#### Manual Download & Install
```bash
# Download the installer
curl -O https://github.com/YOUR_USERNAME/YOUR_REPO/raw/main/install.sh
chmod +x install.sh

# Run the installer
./install.sh
```

#### Local Development Setup
If you've cloned the repository:
```bash
# Run the local setup script
./install.sh

# Or use the old setup script if files already exist
./setup_hooks.sh
```

### What the Installer Does
- ✅ Checks dependencies (Python 3.6+, git, curl)
- ✅ Downloads all hook files securely from GitHub
- ✅ Validates Python syntax in all downloaded files
- ✅ Creates backups of existing installations
- ✅ Sets up proper file permissions
- ✅ Configures .gitignore automatically
- ✅ Builds initial project index
- ✅ Uses temporary directories for security

### Manual Configuration
After installation, you can customize by editing `.claude/settings.json` to enable/disable specific hooks.

## 📚 Hook Descriptions

| Hook | Trigger | Purpose |
|------|---------|---------|
| **indexer.py** | After file edits | Updates project index |
| **session_loader.py** | Session start | Loads context |
| **readup_injector.py** | User prompts | Injects project info |
| **todo_persister.py** | Session end | Saves todo state |
| **test_validator.py** | After edits | Validates code |
| **git_smart_committer.py** | Session end | Git reminders |

## 🎯 Usage Examples

### Understanding Your Project
```
You: /readup
Claude: [Automatically loads full project index and provides comprehensive analysis]

You: How is this project organized?
Claude: [Gets injected project structure automatically]
```

### Automatic Indexing
```
You: Create a new module for user authentication
Claude: [Creates file]
[Hook automatically updates index]
[Hook validates syntax]
```

### Session Continuity
```
# Session 1
You: Add these features [creates todos]
Claude: [Works on tasks]
[Session ends - todos saved]

# Session 2
Claude: [Automatically loads pending todos from last session]
```

## 🛠️ Customization

### Add More Patterns to Readup Injector
Edit `.claude/hooks/readup_injector.py` and add patterns:
```python
patterns = [
    r'/readup',
    r'your_pattern_here',
]
```

### Modify Index Categories
Edit `.claude/hooks/indexer.py` to track additional file types or metadata.

### Create Your Own Hooks
1. Create a new Python script in `.claude/hooks/`
2. Add it to `.claude/settings.json`
3. Make it executable with `chmod +x`

## 📊 What Gets Indexed

The `.claude/.index.json` file contains:
- Complete file structure
- File types and purposes
- Import/export relationships
- Dependency graph
- Critical files list
- Entry points
- Test files
- Statistics

## 🔐 Privacy & Security

- All hooks run locally in your environment
- No data is sent externally
- `.index.json` is gitignored by default
- Sensitive files can be excluded in the indexer

## 💡 Best Practices

1. **Run initial index**: `python3 .claude/hooks/indexer.py`
2. **Keep hooks updated**: Pull latest improvements
3. **Customize patterns**: Adjust to your workflow
4. **Review index**: Check `.claude/.index.json` periodically
5. **Use /readup**: When starting work on unfamiliar code

## 🐛 Troubleshooting

### Hooks not running?
```bash
# Check if executable
ls -la .claude/hooks/

# Test manually
python3 .claude/hooks/session_loader.py

# Check Claude Code debug mode
claude --debug
```

### Index not updating?
```bash
# Manually trigger
python3 .claude/hooks/indexer.py

# Check for errors
cat .claude/.index.json
```

## 🚀 Advanced Features

### Global Installation
To use these hooks across all projects:
```bash
# Copy to user settings
cp -r .claude/hooks ~/.claude/hooks/
cp .claude/settings.json ~/.claude/settings.json
```

### Project-Specific Overrides
Keep project-specific hooks in `.claude/settings.local.json`

## 📈 Benefits

- **Better Context**: Claude understands your project structure instantly
- **Faster Development**: No need to repeatedly explain project layout
- **Continuity**: Pick up where you left off between sessions
- **Quality**: Automatic validation catches issues early
- **Efficiency**: Smart suggestions and automation

## 🤝 Contributing

Feel free to enhance these hooks for your specific needs. Common additions:
- Language-specific analyzers
- Custom validation rules
- Integration with your tools
- Team-specific workflows

---

**Remember**: These hooks are meant to enhance, not replace, good communication with Claude. Always provide clear requirements and context for best results!