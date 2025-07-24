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

# Business Tools Browser Installer for RHEL 9
# This script installs the Business Tools Browser application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="Business Tools Browser"
INSTALL_DIR="."
DESKTOP_FILE="business-tools-browser.desktop"
MENU_DIR="/usr/share/applications"
ICON_DIR="/usr/share/pixmaps"
BIN_DIR="/usr/local/bin"

echo
echo
echo
echo

# Check if running as root
if [[ $EUID -ne 0 ]]; then
 echo
 exit 1
fi

# Check RHEL version
if ! grep -q "${COMPANY_NAME} Enterprise Linux.*9" /etc/${COMPANY_NAME}-release 2>/dev/null; then
 echo
 echo
 echo
fi

# Function to print status
print_status() {
 echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
 echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
 echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Python 3 is installed
print_status "Checking Python 3 installation..."
if ! command -v python3 &> /dev/null; then
 print_error "Python 3 is not installed"
 echo "Installing Python 3..."
 dnf install -y python3 python3-pip python3-tkinter
else
 print_status "Python 3 is installed"
fi

# Check and install required Python packages
print_status "Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install pandas requests openpyxl

# Create installation directory
print_status "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/src"
mkdir -p "$INSTALL_DIR/data"
mkdir -p "$INSTALL_DIR/resources"

# Get the script directory (where installer is located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Copy application files
print_status "Installing application files..."

# Copy main application
if [ -f "$SCRIPT_DIR/src/business_tools_app.py" ]; then
 cp "$SCRIPT_DIR/src/business_tools_app.py" "$INSTALL_DIR/src/"
 chmod +x "$INSTALL_DIR/src/business_tools_app.py"
else
 print_error "Main application file not found: $SCRIPT_DIR/src/business_tools_app.py"
 exit 1
fi

# Copy launcher
if [ -f "$SCRIPT_DIR/business_tools.py" ]; then
 cp "$SCRIPT_DIR/business_tools.py" "$INSTALL_DIR/"
 chmod +x "$INSTALL_DIR/business_tools.py"
else
 print_error "Launcher file not found: $SCRIPT_DIR/business_tools.py"
 exit 1
fi

# Copy desktop file
if [ -f "$SCRIPT_DIR/resources/$DESKTOP_FILE" ]; then
 cp "$SCRIPT_DIR/resources/$DESKTOP_FILE" "$INSTALL_DIR/resources/"
else
 print_error "Desktop file not found: $SCRIPT_DIR/resources/$DESKTOP_FILE"
 exit 1
fi

# Create a simple icon if one doesn't exist
ICON_FILE="$INSTALL_DIR/resources/business_tools.png"
if [ ! -f "$ICON_FILE" ]; then
 print_status "Creating default icon..."
 # Create a simple SVG icon and convert to PNG if imagemagick is available
 if command -v convert &> /dev/null; then
 cat > /tmp/business_tools.svg << 'EOF'
<svg width="48" height="48" xmlns="http://www.w3.org/2000/svg">
 <rect width="48" height="48" fill="#4285f4" rx="6"/>
 <text x="24" y="30" text-anchor="middle" fill="white" font-family="Arial" font-size="16" font-weight="bold">BT</text>
</svg>
EOF
 convert /tmp/business_tools.svg "$ICON_FILE" 2>/dev/null || {
 print_warning "Could not create PNG icon, using default"
 touch "$ICON_FILE"
 }
 rm -f /tmp/business_tools.svg
 else
 print_warning "ImageMagick not available, creating placeholder icon"
 touch "$ICON_FILE"
 fi
fi

# Install desktop file to system menu
print_status "Installing desktop menu entry..."
cp "$INSTALL_DIR/resources/$DESKTOP_FILE" "$MENU_DIR/"
chmod 644 "$MENU_DIR/$DESKTOP_FILE"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
 update-desktop-database "$MENU_DIR"
fi

# Create symbolic link for command line access
print_status "Creating command line launcher..."
ln -sf "$INSTALL_DIR/business_tools.py" "$BIN_DIR/business-tools"
chmod +x "$BIN_DIR/business-tools"

# Set proper permissions
print_status "Setting permissions..."
chown -R root:root "$INSTALL_DIR"
chmod -R 755 "$INSTALL_DIR"
chmod 644 "$INSTALL_DIR/resources/$DESKTOP_FILE"

# Create uninstaller
print_status "Creating uninstaller..."
cat > "$INSTALL_DIR/uninstall.sh" << 'EOF'
#!/bin/bash
# Business Tools Browser Uninstaller

echo "Uninstalling Business Tools Browser..."

# Remove installation directory
rm -rf .

# Remove desktop file
rm -f /usr/share/applications/business-tools-browser.desktop

# Remove command line launcher
rm -f /usr/local/bin/business-tools

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
 update-desktop-database /usr/share/applications
fi

echo "Business Tools Browser has been uninstalled."
EOF

chmod +x "$INSTALL_DIR/uninstall.sh"

# Create sample data file if user has Excel file
print_status "Setting up data directory..."
if [ -f "$SCRIPT_DIR/../python/*.xlsx" ]; then
 print_status "Found Excel data file, copying..."
 cp "$SCRIPT_DIR/../python/*.xlsx" "$INSTALL_DIR/data/"
fi

# Create documentation
print_status "Creating documentation..."
cat > "$INSTALL_DIR/README.md" << 'EOF'
# Business Tools Browser

A comprehensive application for browsing and searching business tools databases.

## Features

- **GUI Interface**: User-friendly graphical interface with search and filtering
- **CLI Interface**: Command-line interface for terminal users
- **Data Processing**: Import and process Excel files with tool information
- **Access Control**: Classify tools as Internal or Public
- **Search & Filter**: Search by name, description, category, and access level

## Usage

### GUI Mode (Default)
```bash
business-tools
# or
./business_tools.py
```

### CLI Mode
```bash
business-tools --cli
# or
./business_tools.py --cli
```

### Process Excel File
```bash
business-tools --process /path/to/file.xlsx
```

## Data Location

- Application data is stored in: `./data/`
- Processed data files: `Cleaned_Tools.csv` and `Tools_Summary.csv`

## Uninstallation

To uninstall the application:
```bash
sudo ./uninstall.sh
```

## Support

For issues or questions, contact your system administrator.
EOF

print_status "Installation completed successfully!"
echo
echo
echo
echo
echo -e "Application installed to: ${BLUE}$INSTALL_DIR${NC}"
echo -e "Menu entry added to: ${BLUE}Applications > Office${NC}"
echo -e "Command line access: ${BLUE}business-tools${NC}"
echo -e "Documentation: ${BLUE}$INSTALL_DIR/README.md${NC}"
echo
echo
echo -e " • Use the Applications menu (Office > Business Tools Browser)"
echo -e " • Or run: ${BLUE}business-tools${NC}"
echo -e " • For CLI mode: ${BLUE}business-tools --cli${NC}"
echo
echo
echo -e " • Run: ${BLUE}sudo $INSTALL_DIR/uninstall.sh${NC}"
echo
print_status "You can now close this terminal and start using Business Tools Browser!"
