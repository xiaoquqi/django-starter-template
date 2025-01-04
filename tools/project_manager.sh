#!/bin/bash

# This script is used to:
# 1. Rename the project name (e.g., from 'mito' to 'newname')
# 2. Rename the Django app directory (e.g., from 'api' to 'newapi')
#
# Usage: 
#   ./project_manager.sh --project-name <new_name>     # Rename project
#   ./project_manager.sh --app-name <new_name>         # Rename Django app
#   ./project_manager.sh --dry-run                     # Show what would be changed
#
# Example: 
#   ./project_manager.sh --project-name myproject --dry-run
#   ./project_manager.sh --app-name myapi --dry-run
#   ./project_manager.sh --project-name myproject --app-name myapi

# Default values
DRY_RUN=false
PROJECT_OLD_NAME="mito"
PROJECT_NEW_NAME=""
APP_OLD_NAME="api"
APP_NEW_NAME=""

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --project-name <name>  New project name (letters and numbers only)"
    echo "  --app-name <name>      New Django app name (letters, numbers and underscores only)"
    echo "  --dry-run             Show what would be changed without making changes"
    echo "  --help                Show this help message"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --project-name)
            PROJECT_NEW_NAME="$2"
            shift 2
            ;;
        --app-name)
            APP_NEW_NAME="$2"
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
            echo "Unknown option: $1"
            show_usage
            ;;
    esac
done

# Validate inputs
if [[ -z "$PROJECT_NEW_NAME" && -z "$APP_NEW_NAME" ]]; then
    echo "Error: Either --project-name or --app-name must be specified"
    show_usage
fi

# Validate project name format
if [[ -n "$PROJECT_NEW_NAME" && ! "$PROJECT_NEW_NAME" =~ ^[a-zA-Z][a-zA-Z0-9_]*$ ]]; then
    echo "Error: Project name must:"
    echo "- Start with a letter" 
    echo "- Only contain letters, numbers and underscores"
    exit 1
fi

# Validate app name format 
if [[ -n "$APP_NEW_NAME" && ! "$APP_NEW_NAME" =~ ^[a-zA-Z][a-zA-Z0-9_]*$ ]]; then
    echo "Error: App name must:"
    echo "- Start with a letter"
    echo "- Only contain letters, numbers and underscores"
    exit 1
fi

# Function to process file content
process_file() {
    local file="$1"
    local changes=false
    local content
    
    content=$(cat "$file")
    
    if [[ -n "$PROJECT_NEW_NAME" ]]; then
        if echo "$content" | grep -q "$PROJECT_OLD_NAME"; then
            changes=true
            if [[ "$DRY_RUN" = true ]]; then
                echo "Would replace '$PROJECT_OLD_NAME' with '$PROJECT_NEW_NAME' in: $file"
            else
                sed -i "s/$PROJECT_OLD_NAME/$PROJECT_NEW_NAME/g" "$file"
                sed -i "s/${PROJECT_OLD_NAME^}/${PROJECT_NEW_NAME^}/g" "$file"
            fi
        fi
    fi
    
    if [[ -n "$APP_NEW_NAME" ]]; then
        if echo "$content" | grep -q "$APP_OLD_NAME"; then
            changes=true
            if [[ "$DRY_RUN" = true ]]; then
                echo "Would replace '$APP_OLD_NAME' with '$APP_NEW_NAME' in: $file"
            else
                # Replace api directory references
                sed -i "s|dockerfile: $APP_OLD_NAME/|dockerfile: $APP_NEW_NAME/|g" "$file"
                sed -i "s|/app/$APP_OLD_NAME|/app/$APP_NEW_NAME|g" "$file"
                sed -i "s|site-packages/$APP_OLD_NAME|site-packages/$APP_NEW_NAME|g" "$file"
                sed -i "s|recursive-include $APP_OLD_NAME|recursive-include $APP_NEW_NAME|g" "$file"
                sed -i "s|flake8 $APP_OLD_NAME|flake8 $APP_NEW_NAME|g" "$file"
                sed -i "s/$APP_OLD_NAME/$APP_NEW_NAME/g" "$file"
            fi
        fi
    fi
    
    return $changes
}

# Function to rename directories and files
rename_items() {
    if [[ -n "$PROJECT_NEW_NAME" ]]; then
        find . -depth -name "*$PROJECT_OLD_NAME*" -not -path "*/\.*" -not -name "$(basename $0)" | while read oldname; do
            newname=$(echo "$oldname" | sed "s/$PROJECT_OLD_NAME/$PROJECT_NEW_NAME/g")
            if [ "$oldname" != "$newname" ]; then
                if [[ "$DRY_RUN" = true ]]; then
                    echo "Would rename: $oldname -> $newname"
                else
                    mv "$oldname" "$newname"
                fi
            fi
        done
    fi
    
    if [[ -n "$APP_NEW_NAME" ]]; then
        if [ -d "$APP_OLD_NAME" ]; then
            if [[ "$DRY_RUN" = true ]]; then
                echo "Would rename directory: $APP_OLD_NAME -> $APP_NEW_NAME"
            else
                mv "$APP_OLD_NAME" "$APP_NEW_NAME"
            fi
        else
            echo "Error: Directory '$APP_OLD_NAME' not found"
            exit 1
        fi
    fi
}

# Main execution
if [[ "$DRY_RUN" = true ]]; then
    echo "=== DRY RUN MODE - No changes will be made ==="
fi

# Process all files
find . -type f -not -path "*/\.*" -not -name "README.md" -not -name "$(basename $0)" -print0 | while IFS= read -r -d '' file; do
    process_file "$file"
done

# Rename directories and files
rename_items

if [[ "$DRY_RUN" = true ]]; then
    echo "=== DRY RUN COMPLETE - No changes were made ==="
else
    echo "=== Changes completed successfully ==="
    if [[ -n "$PROJECT_NEW_NAME" ]]; then
        echo "Project renamed from $PROJECT_OLD_NAME to $PROJECT_NEW_NAME"
    fi
    if [[ -n "$APP_NEW_NAME" ]]; then
        echo "App renamed from $APP_OLD_NAME to $APP_NEW_NAME"
        echo "All configuration files have been updated"
    fi
fi