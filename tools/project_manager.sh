#!/bin/bash

# This script is used to:
# 1. Rename the project name (e.g., from 'mito' to 'newname')
# 2. Rename the Django project directory (e.g., from 'mito' to 'newapi')
#
# Usage:
#   ./project_manager_fixed.sh --project-name <new_name>     # Rename project
#   ./project_manager_fixed.sh --django-project-name <new_name>  # Rename Django project
#   ./project_manager_fixed.sh --dry-run                     # Show what would be changed
#
# Example:
#   ./project_manager_fixed.sh --project-name myproject --dry-run
#   ./project_manager_fixed.sh --django-project-name myapi --dry-run
#   ./project_manager_fixed.sh --project-name myproject --django-project-name myapi

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Get absolute path of current directory
CURRENT_PATH=$(cd "$(dirname "$0")/.." && pwd)
cd "$CURRENT_PATH"

# Default values
DRY_RUN=false
PROJECT_OLD_NAME="mito"
PROJECT_NEW_NAME=""
DJANGO_PROJECT_OLD_NAME="mito"
DJANGO_PROJECT_NEW_NAME=""

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'  # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
  --project-name <name>          New project name (letters and numbers only)
  --django-project-name <name>   New Django project name (letters, numbers and underscores only)
  --dry-run                      Show what would be changed without making changes
  --help                         Show this help message

Examples:
  $0 --project-name myproject --dry-run
  $0 --django-project-name myapi --dry-run
  $0 --project-name myproject --django-project-name myapi
EOF
    exit 1
}

# Function to validate name format
validate_name_format() {
    local name="$1"
    local name_type="$2"

    if [[ ! "$name" =~ ^[a-zA-Z][a-zA-Z0-9_]*$ ]]; then
        print_error "$name_type must:"
        print_error "- Start with a letter"
        print_error "- Only contain letters, numbers and underscores"
        exit 1
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --project-name)
            PROJECT_NEW_NAME="$2"
            shift 2
            ;;
        --django-project-name)
            DJANGO_PROJECT_NEW_NAME="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            ;;
    esac
done

# Validate inputs
if [[ -z "$PROJECT_NEW_NAME" && -z "$DJANGO_PROJECT_NEW_NAME" ]]; then
    print_error "Either --project-name or --django-project-name must be specified"
    show_usage
fi

# Validate project name format
if [[ -n "$PROJECT_NEW_NAME" ]]; then
    validate_name_format "$PROJECT_NEW_NAME" "Project name"
fi

# Validate django project name format
if [[ -n "$DJANGO_PROJECT_NEW_NAME" ]]; then
    validate_name_format "$DJANGO_PROJECT_NEW_NAME" "Django project name"
fi

# Function to replace project name in specific files with exact matches
replace_project_name() {
    if [[ -n "$PROJECT_NEW_NAME" ]]; then
        local files_to_replace=(
            "pyproject.toml"
            "env.sample"
            ".env"
            ".gitignore"
            "docker-compose.yml"
            "docker-compose.dev.yml"
            "docker-compose.prod.yml"
            "Dockerfile"
            "docker/nginx/default.conf"
            "mito/core/settings/base.py"
            "mito/core/settings/rest.py"
        )

        if [[ "$DRY_RUN" = true ]]; then
            print_info "Would replace '$PROJECT_OLD_NAME' with '$PROJECT_NEW_NAME' in:"
            for file in "${files_to_replace[@]}"; do
                echo "  - $file"
            done
        else
            # Replace exact matches of project name in specific files
            for file in "${files_to_replace[@]}"; do
                local full_path="${CURRENT_PATH}/${file}"
                if [[ -f "$full_path" ]]; then
                    sed -i "s/\\b${PROJECT_OLD_NAME}/${PROJECT_NEW_NAME}/g" \
                        "$full_path" 2>/dev/null || true
                fi
            done
        fi
    fi
}

# Function to replace Django project name in specific files with exact matches
replace_django_project_name() {
    if [[ -n "$DJANGO_PROJECT_NEW_NAME" ]]; then
        # Define file paths and their corresponding replacement patterns
        declare -A replacements=(
            ["${CURRENT_PATH}/docker-compose.*.yml"]=\
                "dockerfile: ${DJANGO_PROJECT_OLD_NAME}/Dockerfile|dockerfile: ${DJANGO_PROJECT_NEW_NAME}/Dockerfile"
            ["${CURRENT_PATH}/MANIFEST.in"]=\
                "recursive-include ${DJANGO_PROJECT_OLD_NAME}|recursive-include ${DJANGO_PROJECT_NEW_NAME}"
            ["${CURRENT_PATH}/pyproject.toml"]=\
                "packages = \\[\"${DJANGO_PROJECT_OLD_NAME}\"\\]|packages = \\[\"${DJANGO_PROJECT_NEW_NAME}\"\\]"
            ["${CURRENT_PATH}/tox.ini"]=\
                "flake8 ${DJANGO_PROJECT_OLD_NAME}|flake8 ${DJANGO_PROJECT_NEW_NAME}"
            ["${CURRENT_PATH}/Dockerfile"]=\
                "WORKDIR /opt/${DJANGO_PROJECT_OLD_NAME}|WORKDIR /opt/${DJANGO_PROJECT_NEW_NAME}"
            ["${CURRENT_PATH}/Dockerfile"]=\
                "COPY ${DJANGO_PROJECT_OLD_NAME} /opt/${DJANGO_PROJECT_OLD_NAME}|COPY ${DJANGO_PROJECT_NEW_NAME} /opt/${DJANGO_PROJECT_NEW_NAME}"
            ["${CURRENT_PATH}/Dockerfile"]=\
                "/var/cache/${DJANGO_PROJECT_OLD_NAME}|/var/cache/${DJANGO_PROJECT_NEW_NAME}"
        )

        if [[ "$DRY_RUN" = true ]]; then
            # Display files that would be modified
            print_info "Would replace '$DJANGO_PROJECT_OLD_NAME' with '$DJANGO_PROJECT_NEW_NAME' in:"
            for file in "${!replacements[@]}"; do
                echo "  - $file"
            done
            echo "Would rename directory: $DJANGO_PROJECT_OLD_NAME -> $DJANGO_PROJECT_NEW_NAME"
        else
            # Perform replacements in files
            for file_pattern in "${!replacements[@]}"; do
                local pattern="${replacements[$file_pattern]}"
                local search="${pattern%|*}"
                local replace="${pattern#*|}"

                # Use wildcard to match filenames
                for matched_file in $file_pattern; do
                    if [[ -f "$matched_file" ]]; then
                        sed -i "s|$search|$replace|g" "$matched_file" 2>/dev/null || true
                    fi
                done
            done

            # Rename Django project directory using absolute path
            if [[ -d "${CURRENT_PATH}/${DJANGO_PROJECT_OLD_NAME}" ]]; then
                mv "${CURRENT_PATH}/${DJANGO_PROJECT_OLD_NAME}" \
                   "${CURRENT_PATH}/${DJANGO_PROJECT_NEW_NAME}"
            else
                print_error "Directory '${CURRENT_PATH}/${DJANGO_PROJECT_OLD_NAME}' not found"
                exit 1
            fi
        fi
    fi
}

# Function to replace container and network names
replace_container_names() {
    if [[ -n "$PROJECT_NEW_NAME" ]]; then
        local files_to_replace=(
            "docker-compose.yml"
            "docker-compose.dev.yml"
            "docker-compose.prod.yml"
            "docker/nginx/default.conf"
        )

        if [[ "$DRY_RUN" = true ]]; then
            print_info "Would replace container and network names:"
            for file in "${files_to_replace[@]}"; do
                echo "  - $file"
            done
        else
            # Replace container names and network names
            for file in "${files_to_replace[@]}"; do
                local full_path="${CURRENT_PATH}/${file}"
                if [[ -f "$full_path" ]]; then
                    # Replace container names
                    sed -i "s/${PROJECT_OLD_NAME}-api/${PROJECT_NEW_NAME}-api/g" \
                        "$full_path" 2>/dev/null || true
                    sed -i "s/${PROJECT_OLD_NAME}-worker/${PROJECT_NEW_NAME}-worker/g" \
                        "$full_path" 2>/dev/null || true
                    sed -i "s/${PROJECT_OLD_NAME}-scheduler/${PROJECT_NEW_NAME}-scheduler/g" \
                        "$full_path" 2>/dev/null || true
                    sed -i "s/${PROJECT_OLD_NAME}-nginx/${PROJECT_NEW_NAME}-nginx/g" \
                        "$full_path" 2>/dev/null || true
                    sed -i "s/${PROJECT_OLD_NAME}-mariadb/${PROJECT_NEW_NAME}-mariadb/g" \
                        "$full_path" 2>/dev/null || true
                    sed -i "s/${PROJECT_OLD_NAME}-redis/${PROJECT_NEW_NAME}-redis/g" \
                        "$full_path" 2>/dev/null || true
                    sed -i "s/${PROJECT_OLD_NAME}-flower/${PROJECT_NEW_NAME}-flower/g" \
                        "$full_path" 2>/dev/null || true

                    # Replace network names
                    sed -i "s/${PROJECT_OLD_NAME}_network/${PROJECT_NEW_NAME}_network/g" \
                        "$full_path" 2>/dev/null || true

                    # Replace volume paths
                    sed -i "s|/opt/${PROJECT_OLD_NAME}|/opt/${PROJECT_NEW_NAME}|g" \
                        "$full_path" 2>/dev/null || true
                fi
            done
        fi
    fi
}

# Main execution
if [[ "$DRY_RUN" = true ]]; then
    print_info "=== DRY RUN MODE - No changes will be made ==="
fi

# Execute based on provided options
if [[ -n "$PROJECT_NEW_NAME" ]]; then
    replace_project_name
    replace_container_names
fi

if [[ -n "$DJANGO_PROJECT_NEW_NAME" ]]; then
    replace_django_project_name
fi

if [[ "$DRY_RUN" = true ]]; then
    print_info "=== DRY RUN COMPLETE - No changes were made ==="
else
    print_info "=== Changes completed successfully ==="
    if [[ -n "$PROJECT_NEW_NAME" ]]; then
        print_info "Project renamed from $PROJECT_OLD_NAME to $PROJECT_NEW_NAME"
    fi
    if [[ -n "$DJANGO_PROJECT_NEW_NAME" ]]; then
        print_info "Django project renamed from $DJANGO_PROJECT_OLD_NAME to $DJANGO_PROJECT_NEW_NAME"
        print_info "All configuration files have been updated"
    fi
fi