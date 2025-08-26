#!/bin/bash
set -euo pipefail

# Claude Code Enhanced Hook System - Secure Installation Script
# This script can be run via: curl -sSL <URL> | bash

# Configuration
REPO_URL="${CLAUDE_HOOKS_REPO:-https://github.com/justanotherspy/index}"
BRANCH="${CLAUDE_HOOKS_BRANCH:-main}"
INSTALL_DIR=".claude"
TEMP_DIR=""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1" >&2; }

# Cleanup function
cleanup() {
    if [[ -n "${TEMP_DIR}" && -d "${TEMP_DIR}" ]]; then
        rm -rf "${TEMP_DIR}"
    fi
}
trap cleanup EXIT

# Check if running in a pipe (curl | bash)
check_pipe() {
    if [[ -t 0 ]]; then
        log_error "This script should be run via: curl -sSL <URL> | bash"
        log_error "Or download and run: ./install_index.sh"
        exit 1
    fi
}

# Check dependencies
check_dependencies() {
    local missing_deps=()
    
    # Check for required commands
    for cmd in python3 git curl; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done
    
    # Check for optional but recommended jq
    if ! command -v jq &> /dev/null; then
        log_warn "jq is not installed (optional but recommended for better output)"
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        log_error "Please install them and try again"
        exit 1
    fi
    
    # Check Python version (3.6+)
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 6) else 1)" 2>/dev/null; then
        log_error "Python 3.6 or higher is required"
        exit 1
    fi
    
    log_info "All dependencies satisfied"
}

# Create safe temporary directory
create_temp_dir() {
    TEMP_DIR=$(mktemp -d -t claude-hooks-XXXXXX) || {
        log_error "Failed to create temporary directory"
        exit 1
    }
    log_info "Created temporary directory: ${TEMP_DIR}"
}

# Download files from repository
download_files() {
    local base_url="${REPO_URL/github.com/raw.githubusercontent.com}/${BRANCH}"
    
    log_info "Downloading hook files from repository..."
    
    # Create directory structure
    mkdir -p "${TEMP_DIR}/.claude/hooks"
    mkdir -p "${TEMP_DIR}/.claude/commands"
    
    # List of files to download
    local files=(
        ".claude/settings.json"
        ".claude/hooks/indexer.py"
        ".claude/hooks/session_loader.py"
        ".claude/hooks/readup_injector.py"
        ".claude/hooks/test_validator.py"
        ".claude/hooks/todo_persister.py"
        ".claude/hooks/git_smart_committer.py"
        ".claude/hooks/context_optimizer.py"
        ".claude/hooks/manual_index.py"
        ".claude/commands/readup.md"
        "HOOKS_README.md"
    )
    
    # Download each file
    for file in "${files[@]}"; do
        local url="${base_url}/${file}"
        local dest="${TEMP_DIR}/${file}"
        
        if curl -sSL --fail -o "${dest}" "${url}" 2>/dev/null; then
            echo "  Downloaded: ${file}"
        else
            log_warn "Could not download ${file} (might not exist yet)"
        fi
    done
    
    log_info "Download complete"
}

# Validate downloaded files
validate_files() {
    log_info "Validating downloaded files..."
    
    # Check for minimum required files
    local required_files=(
        "${TEMP_DIR}/.claude/settings.json"
        "${TEMP_DIR}/.claude/hooks/indexer.py"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "${file}" ]]; then
            log_error "Required file missing: ${file}"
            log_error "Repository might not be properly set up"
            exit 1
        fi
    done
    
    # Basic Python syntax check
    for py_file in "${TEMP_DIR}/.claude/hooks"/*.py; do
        if [[ -f "${py_file}" ]]; then
            if ! python3 -m py_compile "${py_file}" 2>/dev/null; then
                log_error "Python syntax error in $(basename "${py_file}")"
                exit 1
            fi
        fi
    done
    
    log_info "All files validated successfully"
}

# Backup existing installation
backup_existing() {
    if [[ -d "${INSTALL_DIR}" ]]; then
        local backup_dir
        backup_dir="${INSTALL_DIR}.backup.$(date +%Y%m%d-%H%M%S)"
        log_warn "Existing installation found, backing up to ${backup_dir}"
        cp -r "${INSTALL_DIR}" "${backup_dir}"
    fi
}

# Install files
install_files() {
    log_info "Installing hook system..."
    
    # Create installation directory
    mkdir -p "${INSTALL_DIR}"
    
    # Copy files from temp to installation directory
    if [[ -d "${TEMP_DIR}/.claude" ]]; then
        cp -r "${TEMP_DIR}/.claude"/* "${INSTALL_DIR}/"
    fi
    
    # Copy README if it exists
    if [[ -f "${TEMP_DIR}/HOOKS_README.md" ]]; then
        cp "${TEMP_DIR}/HOOKS_README.md" ./
    fi
    
    # Make Python scripts executable
    chmod +x "${INSTALL_DIR}/hooks"/*.py 2>/dev/null || true
    
    log_info "Files installed successfully"
}

# Configure gitignore
configure_gitignore() {
    local gitignore_entries=(
        ".claude/.index.json"
        ".claude/.todo_state.json"
        ".claude/bash_history.log"
        ".claude/settings.local.json"
        ".claude/*.backup.*"
    )
    
    if [[ -f .gitignore ]]; then
        log_info "Updating .gitignore..."
        for entry in "${gitignore_entries[@]}"; do
            if ! grep -qF "${entry}" .gitignore; then
                echo "${entry}" >> .gitignore
            fi
        done
    else
        log_info "Creating .gitignore..."
        printf "%s\n" "${gitignore_entries[@]}" > .gitignore
    fi
}

# Run initial indexing
run_initial_index() {
    log_info "Building initial project index..."
    
    if python3 "${INSTALL_DIR}/hooks/indexer.py" 2>/dev/null; then
        if [[ -f "${INSTALL_DIR}/.index.json" ]]; then
            if command -v jq &> /dev/null; then
                local file_count
                file_count=$(jq -r '.stats.total_files' "${INSTALL_DIR}/.index.json" 2>/dev/null || echo "unknown")
                log_info "Project indexed successfully (${file_count} files)"
            else
                log_info "Project indexed successfully"
            fi
        fi
    else
        log_warn "Initial indexing failed - you can run it manually later"
    fi
}

# Print success message
print_success() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 Claude Code Hook System installed successfully!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📋 Next Steps:"
    echo "  1. Restart Claude Code to load the hooks"
    echo "  2. Try: /readup - to analyze your project"
    echo "  3. Edit any file to see automatic indexing"
    echo ""
    echo "📚 Documentation: HOOKS_README.md"
    echo "🔧 Configuration: .claude/settings.json"
    echo ""
}

# Main installation flow
main() {
    echo "🚀 Claude Code Enhanced Hook System - Secure Installer"
    echo "======================================================"
    echo ""
    
    # Don't check pipe for local execution
    # check_pipe
    
    # Check all dependencies first
    check_dependencies
    
    # Create temporary directory for downloads
    create_temp_dir
    
    # Download files from repository
    download_files
    
    # Validate downloaded files
    validate_files
    
    # Backup existing installation if present
    backup_existing
    
    # Install files
    install_files
    
    # Configure gitignore
    configure_gitignore
    
    # Run initial indexing
    run_initial_index
    
    # Print success message
    print_success
}

# Run main function
main "$@"