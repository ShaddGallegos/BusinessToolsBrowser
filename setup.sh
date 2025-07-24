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

# Quick Setup Script for Business Tools Browser
# This script prepares the application for installation

echo "Setting up Business Tools Browser..."

# Make scripts executable
chmod +x install.sh
chmod +x business_tools.py
chmod +x src/business_tools_app.py

# Copy any existing data files
if [ -f "../python/*.xlsx" ]; then
 echo "Copying existing Excel data file..."
 cp "../python/*.xlsx" data/
fi

if [ -f "../python/Cleaned_Tools.csv" ]; then
 echo "Copying existing cleaned data..."
 cp "../python/Cleaned_Tools.csv" data/
fi

echo "Setup complete!"
echo ""
echo "To install system-wide (requires sudo):"
echo " sudo ./install.sh"
echo ""
echo "To run locally without installing:"
echo " python3 business_tools.py"
echo " python3 business_tools.py --cli"
