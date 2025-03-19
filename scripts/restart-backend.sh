#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Get current timestamp
get_timestamp() {
    date "+%Y-%m-%d %H:%M:%S"
}

# Print formatted log messages
log_info() {
    echo -e "${GRAY}[$(get_timestamp)]${NC} ${GREEN}[INFO]${NC}    $1"
}

log_success() {
    echo -e "${GRAY}[$(get_timestamp)]${NC} ${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${GRAY}[$(get_timestamp)]${NC} ${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${GRAY}[$(get_timestamp)]${NC} ${RED}[ERROR]${NC}   $1"
}

log_step() {
    echo -e "\n${GRAY}[$(get_timestamp)]${NC} ${BLUE}[STEP]${NC}    ${BOLD}$1${NC}"
}

log_debug() {
    if [[ "${DEBUG}" == "true" ]]; then
        echo -e "${GRAY}[$(get_timestamp)]${NC} ${MAGENTA}[DEBUG]${NC}   $1"
    fi
}

log_section() {
    echo -e "\n${CYAN}════════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════════════════${NC}\n"
}

# Load configuration from .env file
load_env() {
    if [ -f .env ]; then
        # Load necessary environment variables
        export LOCAL_BASE_DIR=$(grep '^LOCAL_BASE_DIR=' .env | cut -d '=' -f2)
    else
        log_error ".env file not found!"
        return 1
    fi
}

# Main function to restart backend services
restart_backend() {
    local force=false
    
    # Parse arguments
    while [[ "$#" -gt 0 ]]; do
        case $1 in
            --force) force=true ;;
            *) log_error "Unknown parameter: $1"; return 1 ;;
        esac
        shift
    done
    
    log_step "Restarting backend services..."
    
    # Load environment variables
    if ! load_env; then
        return 1
    fi
    
    # If --force parameter is used, clear data folder
    if [ "$force" = true ]; then
        log_warning "Force restart mode: This will clear the data folder, all data will be deleted!"
        read -p "Are you sure you want to continue? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Clearing data folder..."
            rm -rf "${LOCAL_BASE_DIR}/data"
            log_success "Data folder cleared, database will be reinitialized"
        else
            log_info "Operation cancelled"
            return 0
        fi
    fi
    
    # 1. Stop backend service
    BACKEND_PID=$(lsof -ti:8002)
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID
        log_success "Backend service stopped"
    fi
    rm -f run/.backend.pid backend.log
    
    # 2. Wait for port release
    sleep 2
    
    # 3. Start backend service
    ./scripts/start.sh --backend-only
}

# Execute restart service
restart_backend "$@"
