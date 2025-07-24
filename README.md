# Business Tools Browser

A comprehensive, unified application for browsing, searching, and managing business tools databases. This application combines data processing, GUI interface, and CLI functionality into a single, easy-to-install package.

## Features

### [INFO] Unified Application
- **Single executable** combining all functionality
- **Dual interface**: Both GUI and CLI modes
- **Integrated data processing** for Excel files
- **Professional business interface** without emojis

### [INFO] Advanced Search & Filtering
- **Real-time search** across tool names and descriptions
- **Category filtering** by tool type
- **Access level filtering** (Internal/Public tools)
- **Combined filters** for precise results

### [INFO] Access Control
- **Internal Tools**: Company-only tools and resources
- **Public Tools**: Publicly accessible tools
- **Automatic classification** based on URL and content analysis

### [INFO] Data Management
- **Excel file import** with automatic processing
- **CSV export** of cleaned data
- **URL validation** to ensure accessibility
- **Enhanced descriptions** and categorization

## Installation

### System Requirements
- **RHEL 9** (Red Hat Enterprise Linux 9)
- **Python 3.6+** with tkinter support
- **Internet connection** for URL validation

### Quick Install (Recommended)
```bash
# Make installer executable
chmod +x install.sh

# Run installer (requires sudo)
sudo ./install.sh
```

### Manual Setup (Development)
```bash
# Setup for local development
chmod +x setup.sh
./setup.sh

# Install Python dependencies
pip3 install -r requirements.txt

# Run locally
python3 business_tools.py
```

## Usage

### GUI Mode (Default)
Start the graphical interface:
```bash
business-tools
```
Or from the Applications menu: **Office > Business Tools Browser**

#### GUI Features:
- **Search bar**: Type keywords to search tool names and descriptions
- **Category dropdown**: Filter by tool category (Security, Education, etc.)
- **Access filter**: Show only Internal, Public, or All tools
- **Double-click**: Open tool URL in web browser
- **Load File button**: Import new Excel files
- **Real-time filtering**: Results update as you type

### CLI Mode
Start the command-line interface:
```bash
business-tools --cli
```

#### CLI Features:
- **Browse all tools**: View complete tool list
- **Search functionality**: Enter keywords to find tools
- **Category browsing**: Browse tools by category
- **Access level browsing**: Browse Internal or Public tools
- **File processing**: Load new Excel files
- **Statistics**: View data summaries

### Data Processing Only
Process an Excel file without starting the interface:
```bash
business-tools --process /path/to/file.xlsx
```

## File Structure

```
/opt/BusinessToolsBrowser/
 business_tools.py # Main launcher
 src/
 business_tools_app.py # Unified application code
 data/ # Data files
 Cleaned_Tools.csv # Processed tool data
 Tools_Summary.csv # Category summaries
 *.xlsx # Original Excel files
 resources/ # Application resources
 business-tools-browser.desktop
 business_tools.png # Application icon
 requirements.txt # Python dependencies
 uninstall.sh # Uninstaller script
 README.md # This file
```

## Data Format

The application expects Excel files with these columns:
- **Name**: Tool name
- **URL**: Tool website/link
- **Synopsis/Description**: Tool description
- **Tool_Type/Category**: Tool category

Alternative column names are automatically mapped:
- `Url`, `Link`, `Links` → `URL`
- `Tool_Name`, `Title` → `Name`
- `Description` → `Synopsis`
- `Type`, `Category` → `Tool_Type`

## Access Level Classification

Tools are automatically classified as:

### Internal Tools
- URLs containing: `redhat.com`, `internal`, `intranet`, `corp`
- Descriptions mentioning: `employee`, `staff`, `private`, `restricted`

### Public Tools
- All other tools not matching internal criteria
- Publicly accessible websites and services

## Categories

Tools are automatically categorized into:
- **Security**: Authentication, identity, tokens
- **Education**: Learning, labs, training materials
- **Diagramming**: Flowcharts, architecture diagrams
- **Media Tools**: Video, streaming, recording utilities
- **Code Repositories**: Git, source control
- **Meetings**: Conference, collaboration tools
- **Automation**: Ansible, workflow tools
- **CLI Utilities**: Terminal, command-line tools
- **General Utilities**: Other business tools

## Troubleshooting

### Installation Issues
```bash
# Check Python installation
python3 --version

# Install missing dependencies
sudo dnf install python3 python3-pip python3-tkinter

# Install Python packages
pip3 install pandas requests openpyxl
```

### GUI Won't Start
```bash
# Check if tkinter is available
python3 -c "import tkinter; print('GUI available')"

# If failed, install tkinter
sudo dnf install python3-tkinter
```

### Permission Errors
```bash
# Fix permissions
sudo chown -R root:root /opt/BusinessToolsBrowser
sudo chmod -R 755 /opt/BusinessToolsBrowser
```

### Data Processing Errors
- Ensure Excel file has required columns (Name, URL, Synopsis)
- Check file permissions and accessibility
- Verify internet connection for URL validation

## Uninstallation

To completely remove the application:
```bash
sudo /opt/BusinessToolsBrowser/uninstall.sh
```

This removes:
- Application files from `/opt/BusinessToolsBrowser/`
- Desktop menu entry
- Command-line launcher from `/usr/local/bin/`

## Development

### File Organization
- **src/business_tools_app.py**: Main application with all classes
- **business_tools.py**: Simple launcher script
- **install.sh**: Complete installer for RHEL 9
- **setup.sh**: Development setup script

### Key Classes
- **DataProcessor**: Handles Excel processing and data cleaning
- **BusinessToolsGUI**: Tkinter-based graphical interface
- **BusinessToolsCLI**: Command-line interface

### Adding Features
The unified application design makes it easy to:
- Add new data sources
- Extend search functionality
- Add new categorization rules
- Customize the interface

## Support

For issues, questions, or feature requests:
1. Check the troubleshooting section above
2. Verify system requirements are met
3. Contact your system administrator
4. Check application logs in `/opt/BusinessToolsBrowser/data/`

## License

This application is designed for internal business use. Please ensure compliance with your organization's software policies.
