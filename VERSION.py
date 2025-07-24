#!/usr/bin/env python3
"""
User-configurable variables - modify as needed
"""
import os
import getpass

# User configuration
USER = os.getenv('USER', getpass.getuser())
USER_EMAIL = os.getenv('USER_EMAIL', f"{USER}@{os.getenv('COMPANY_DOMAIN', 'example.com')}")
COMPANY_NAME = os.getenv('COMPANY_NAME', 'Your Company')
COMPANY_DOMAIN = os.getenv('COMPANY_DOMAIN', 'example.com')

"""
User-configurable variables - modify as needed
"""
import os
import getpass

# User configuration
USER = os.getenv('USER', getpass.getuser())
USER_EMAIL = os.getenv('USER_EMAIL', f"{USER}@{os.getenv('COMPANY_DOMAIN', 'example.com')}")
COMPANY_NAME = os.getenv('COMPANY_NAME', 'Your Company')
COMPANY_DOMAIN = os.getenv('COMPANY_DOMAIN', 'example.com')

# Business Tools Browser - Version Information

VERSION = "1.0.0"
BUILD_DATE = "2025-07-22"
DESCRIPTION = "Unified Business Tools Browser Application"

# Changelog
CHANGELOG = """
Version 1.0.0 (2025-07-22)
- Initial release
- Unified application combining GUI, CLI, and data processing
- RHEL 9 installer with desktop integration
- Access level classification (Internal/Public)
- Professional business interface without emojis
- Advanced search and filtering capabilities
- Automatic Excel file processing
- URL validation and categorization
"""
