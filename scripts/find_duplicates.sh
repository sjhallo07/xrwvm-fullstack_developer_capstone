#!/bin/bash
#
# find_duplicates.sh - Detect duplicate files by MD5 hash and optionally delete duplicates.
#
# Usage:
#   ./scripts/find_duplicates.sh [--check|--delete]
#
# Options:
#   --check   (default) Report duplicate files without deleting
#   --delete  Delete duplicate files (WARNING: Use with caution and review before deleting)
#
# Description:
#   This script scans the repository for duplicate files by computing MD5 hashes.
#   By default, it only reports duplicates. Use --delete to remove duplicates after review.
#

set -e

MODE="${1:---check}"

if [[ "$MODE" != "--check" && "$MODE" != "--delete" ]]; then
    echo "Error: Invalid option '$MODE'"
    echo "Usage: $0 [--check|--delete]"
    exit 1
fi

echo "==================================="
echo "  Duplicate File Detection Tool"
echo "==================================="
echo "Mode: $MODE"
echo ""

# Find all files (excluding .git directory and common binary/build artifacts)
echo "Scanning for files..."
FILES=$(find . -type f \
    -not -path "./.git/*" \
    -not -path "*/node_modules/*" \
    -not -path "*/dist/*" \
    -not -path "*/build/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*.pyc" \
    2>/dev/null)

if [[ -z "$FILES" ]]; then
    echo "No files found to check."
    exit 0
fi

# Compute MD5 hashes and group duplicates
echo "Computing MD5 hashes..."
TEMP_FILE=$(mktemp)

while IFS= read -r file; do
    if [[ -f "$file" ]]; then
        hash=$(md5sum "$file" 2>/dev/null | awk '{print $1}')
        if [[ -n "$hash" ]]; then
            echo "$hash $file" >> "$TEMP_FILE"
        fi
    fi
done <<< "$FILES"

# Find and report duplicates
echo ""
echo "Analyzing for duplicates..."
DUPLICATES=$(sort "$TEMP_FILE" | awk '
{
    hash = $1
    file = substr($0, index($0, $2))
    files[hash] = files[hash] (files[hash] ? "\n" : "") file
    count[hash]++
}
END {
    found = 0
    for (hash in count) {
        if (count[hash] > 1) {
            found = 1
            print "Hash: " hash " (" count[hash] " duplicates)"
            print files[hash]
            print ""
        }
    }
    if (!found) {
        print "No duplicates found."
    }
}
')

echo "$DUPLICATES"

if [[ "$MODE" == "--delete" ]]; then
    echo ""
    echo "WARNING: Delete mode is enabled!"
    echo "This will delete duplicate files, keeping only the first occurrence."
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " CONFIRM
    
    if [[ "$CONFIRM" != "yes" ]]; then
        echo "Delete operation cancelled."
        rm -f "$TEMP_FILE"
        exit 0
    fi
    
    echo "Deleting duplicates..."
    sort "$TEMP_FILE" | awk '
    {
        hash = $1
        file = substr($0, index($0, $2))
        if (seen[hash]++) {
            print file
        }
    }
    ' | while IFS= read -r duplicate; do
        if [[ -f "$duplicate" ]]; then
            echo "Deleting: $duplicate"
            rm "$duplicate"
        fi
    done
    
    echo "Deletion complete."
fi

# Cleanup
rm -f "$TEMP_FILE"

echo ""
echo "Done."
