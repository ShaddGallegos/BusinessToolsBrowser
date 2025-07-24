#!/bin/bash
# User-configurable variables - modify as needed
USER="${USER}"
USER_EMAIL="${USER}@${COMPANY_DOMAIN:-example.com}"
COMPANY_NAME="${COMPANY_NAME:-Your Company}"
COMPANY_DOMAIN="${COMPANY_DOMAIN:-example.com}"

# User-configurable variables - modify as needed
USER="${USER}"
USER_EMAIL="${USER}@${COMPANY_DOMAIN:-example.com}"
COMPANY_NAME="${COMPANY_NAME:-Your Company}"
COMPANY_DOMAIN="${COMPANY_DOMAIN:-example.com}"

# Migration script to clean up and organize Business Tools files

echo "Business Tools Migration and Cleanup Script"
echo "==========================================="

# Set directories
OLD_DIR="."
NEW_DIR="."

echo "Migrating from: $OLD_DIR"
echo " to: $NEW_DIR"
echo

# Check if directories exist
if [ ! -d "$OLD_DIR" ]; then
 echo "Error: Old directory not found: $OLD_DIR"
 exit 1
fi

if [ ! -d "$NEW_DIR" ]; then
 echo "Error: New directory not found: $NEW_DIR"
 exit 1
fi

# Copy any missing data files
echo "1. Copying data files..."
cp "$OLD_DIR"/*.csv "$NEW_DIR/data/" 2>/dev/null || echo " No CSV files to copy"
cp "$OLD_DIR"/*.xlsx "$NEW_DIR/data/" 2>/dev/null || echo " No Excel files to copy"

# Copy documentation if newer
echo "2. Checking documentation..."
if [ -f "$OLD_DIR/README_Business_Tools.md" ]; then
 if [ ! -f "$NEW_DIR/README_Business_Tools.md" ]; then
 cp "$OLD_DIR/README_Business_Tools.md" "$NEW_DIR/"
 echo " Copied README_Business_Tools.md"
 fi
fi

# Archive old scripts for reference
echo "3. Creating archive of old scripts..."
mkdir -p "$NEW_DIR/archive"
cp "$OLD_DIR"/*.py "$NEW_DIR/archive/" 2>/dev/null || echo " No Python files to archive"

# List what we now have
echo "4. Current organized structure:"
echo " Data files:"
ls "$NEW_DIR/data/" | sed 's/^/ /'
echo " Main application:"
ls "$NEW_DIR"/*.py | sed 's/^/ /'
echo " Archived scripts:"
ls "$NEW_DIR/archive/" | sed 's/^/ /'

echo
echo "Migration complete!"
echo
echo "Next steps:"
echo "1. Test the new unified application: cd $NEW_DIR && python3 business_tools.py"
echo "2. Install system-wide: sudo ./install.sh"
echo "3. Remove old directory: rm -rf $OLD_DIR"
