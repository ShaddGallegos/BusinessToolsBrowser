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

# Cleanup script - Remove unnecessary files and organize the project

echo "Business Tools Browser - Cleanup and Organization"
echo "================================================"

# Current working directory
CURRENT_DIR="."
OLD_DIR="."

echo "[INFO] Starting cleanup process..."
echo

# 1. Remove the old BusinessTools directory (it's been migrated)
if [ -d "$OLD_DIR" ]; then
 echo "1. Removing old BusinessTools directory..."
 rm -rf "$OLD_DIR"
 echo " [INFO] Removed: $OLD_DIR"
else
 echo "1. Old BusinessTools directory already removed"
fi

# 2. Remove the archive directory (old scripts no longer needed)
if [ -d "$CURRENT_DIR/archive" ]; then
 echo "2. Removing archive directory (old scripts)..."
 rm -rf "$CURRENT_DIR/archive"
 echo " [INFO] Removed: archive/ directory"
else
 echo "2. Archive directory already removed"
fi

# 3. Remove temporary/helper scripts that are no longer needed
echo "3. Removing temporary helper scripts..."
TEMP_SCRIPTS=(
 "migrate.sh"
 "final_summary.sh"
 "demo.py"
)

for script in "${TEMP_SCRIPTS[@]}"; do
 if [ -f "$CURRENT_DIR/$script" ]; then
 rm "$CURRENT_DIR/$script"
 echo " [INFO] Removed: $script"
 fi
done

# 4. Remove duplicate documentation
echo "4. Cleaning up documentation..."
if [ -f "$CURRENT_DIR/README_Business_Tools.md" ]; then
 # Keep the main README.md, remove the duplicate
 rm "$CURRENT_DIR/README_Business_Tools.md"
 echo " [INFO] Removed: README_Business_Tools.md (duplicate)"
fi

# 5. Check if any CSV files exist in wrong locations
echo "5. Organizing data files..."
# All data files should be in data/ directory only
find "$CURRENT_DIR" -maxdepth 1 -name "*.csv" -exec mv {} "$CURRENT_DIR/data/" \; 2>/dev/null
find "$CURRENT_DIR" -maxdepth 1 -name "*.xlsx" -exec mv {} "$CURRENT_DIR/data/" \; 2>/dev/null

echo " [INFO] Data files organized in data/ directory"

echo
echo "[INFO] Cleanup Summary:"
echo "=================================="

# Show final structure
echo "[INFO] Final Project Structure:"
echo " [INFO] business_tools.py # Main launcher (UNIFIED APP)"
echo " [INFO] src/business_tools_app.py # Complete application code"
echo " [INFO] data/ # All data files"
for file in "$CURRENT_DIR/data"/*; do
 if [ -f "$file" ]; then
 echo " $(basename "$file")"
 fi
done
echo " [INFO] resources/ # Desktop integration"
echo " [INFO] install.sh # System installer"
echo " [INFO] QUICKSTART.md # Quick start guide"
echo " [INFO] README.md # Documentation"
echo " [INFO] requirements.txt # Dependencies"
echo " [INFO] setup.sh # Local setup"
echo " [INFO] VERSION.py # Version info"

echo
echo "[INFO] Space saved by removing duplicates and old files:"
du -sh "$CURRENT_DIR" | cut -f1 | xargs echo "Total project size:"

echo
echo "[INFO] Cleanup complete!"
echo
echo "[INFO] What remains (essential files only):"
echo "• 1 unified application (business_tools.py + src/business_tools_app.py)"
echo "• Professional installer (install.sh)"
echo "• Documentation (README.md, QUICKSTART.md)"
echo "• Data files (in data/ directory)"
echo "• Dependencies (requirements.txt)"
echo "• Desktop integration (resources/)"
echo
echo "[INFO] Your Business Tools Browser is now clean and optimized!"
echo "Ready for: python3 business_tools.py"
echo "Or install: sudo ./install.sh"
