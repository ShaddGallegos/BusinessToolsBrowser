#!/usr/bin/env python3
"""
Enhanced Business Tools Browser Launcher
Supports multiple file formats, link validation, and master CSV creation
"""
import os
import sys
from pathlib import Path

# Get application directory
APP_DIR = Path(__file__).parent

# Change to app directory and run
os.chdir(APP_DIR)
sys.path.insert(0, str(APP_DIR / "src"))

from src.business_tools_app import main

if __name__ == "__main__":
    main()
