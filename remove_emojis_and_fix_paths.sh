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

# Script to remove emojis/special icons and fix hard-coded paths

echo "Removing emojis and fixing paths across all projects..."

# Function to clean a file
clean_file() {
 local file="$1"
 echo "Processing: $file"
 
 # Create backup
 cp "$file" "$file.backup"
 
 # Remove emojis and special characters (common ones)
 sed -i 's/[[INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO][INFO]]/\[INFO\]/g' "$file"
 sed -i 's/[[MARKER][MARKER][MARKER][MARKER][MARKER][MARKER][MARKER][MARKER][MARKER][MARKER][MARKER][MARKER]]/\[MARKER\]/g' "$file"
 sed -i 's/[[CONTROL][INFO][CONTROL][INFO][CONTROL][INFO][CONTROL][INFO][CONTROL][INFO][INFO][CONTROL][CONTROL]]/\[CONTROL\]/g' "$file"
 sed -i 's/[[ARROW][INFO][ARROW][INFO][ARROW][INFO][ARROW][INFO][ARROW][INFO][ARROW][INFO][ARROW][INFO][ARROW][INFO]]/\[ARROW\]/g' "$file"
 
 # Clean up any remaining emoji patterns
 sed -i 's/[-]//g' "$file" # Remove emoji range
 sed -i 's/[[INFO]-]//g' "$file" # Remove transport/symbols
 sed -i 's/[-]//g' "$file" # Remove misc symbols
 
 # Remove hardcoded paths and make relative
 sed -i 's|.|.|g' "$file"
 sed -i 's|.|.|g' "$file"
 sed -i 's|.|.|g' "$file"
 sed -i 's|.|.|g' "$file" # Keep system install path
 sed -i 's|/usr/share/applications|/usr/share/applications|g' "$file" # Keep system path
 sed -i 's|/usr/local/bin|/usr/local/bin|g' "$file" # Keep system path
 
 # Replace specific filename dependencies
 sed -i 's|Red_Hat_Tools_For_SA_SSP_and_Managers\.xlsx|*.xlsx|g' "$file"
 sed -i 's|"*.xlsx"|find_excel_file()|g' "$file"
 
 echo " Cleaned: $file"
}

# Find and clean all Python and shell script files
find . -name "*.py" -type f | while read file; do
 clean_file "$file"
done

find . -name "*.sh" -type f | while read file; do
 clean_file "$file"
done

# Also clean markdown files
find . -name "*.md" -type f | while read file; do
 clean_file "$file"
done

echo "Emoji and path cleanup complete!"
