#!/usr/bin/env python3
"""
Business Tools Launcher and Manager
Provides comprehensive business tools with URL display capabilities, data processing,
and automatic URL description extraction from Excel/CSV files.

Features:
- Multi-format data import (XLS, XLSX, CSV)
- Automatic URL detection and description extraction
- Interactive data viewer with sorting and search
- Alphabetical data sorting
- Batch processing capabilities
- Automatic dependency installation

Usage:
    python3 business_tools.py [command] [options]
    
Commands:
    gui                    Launch GUI interface
    view <file>           Interactive data viewer
    process <file>        Process and sort data file
    batch <directory>     Batch process directory
    deps                  Install/check dependencies
    help                  Show help information
"""

import os
import getpass
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from pathlib import Path
import webbrowser
import pandas as pd
from typing import Optional, List, Dict, Any
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import time

# User configuration
USER = os.getenv('USER', getpass.getuser())
USER_EMAIL = os.getenv('USER_EMAIL', f"{USER}@{os.getenv('COMPANY_DOMAIN', 'example.com')}")
COMPANY_NAME = os.getenv('COMPANY_NAME', 'Your Company')
COMPANY_DOMAIN = os.getenv('COMPANY_DOMAIN', 'example.com')

# Colors for terminal output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m' # No Color

def print_colored_url(url, description=""):
    """Print URL in blue color with optional description"""
    if description:
        print(f"{description}: {BLUE}{url}{NC}")
    else:
        print(f"{BLUE}{url}{NC}")
    return f"{BLUE}{url}{NC}"

def print_status(message):
    """Print status message in cyan"""
    print(f"{CYAN}[INFO]{NC} {message}")

def print_success(message):
    """Print success message in green"""
    print(f"{GREEN}[SUCCESS]{NC} {message}")

def print_warning(message):
    """Print warning message in yellow"""
    print(f"{YELLOW}[WARNING]{NC} {message}")

def print_error(message):
    """Print error message in red"""
    print(f"{RED}[ERROR]{NC} {message}")

def install_dependencies():
    """Install required dependencies for the business tools"""
    required_packages = [
        'requests',
        'beautifulsoup4',
        'pandas',
        'openpyxl',
        'xlrd'
    ]
    
    print_status("Checking and installing required dependencies...")
    
    for package in required_packages:
        try:
            # Try to import the package
            if package == 'beautifulsoup4':
                import bs4
            elif package == 'openpyxl':
                import openpyxl
            elif package == 'xlrd':
                import xlrd
            else:
                __import__(package)
            print_success(f"✓ {package} already installed")
        except ImportError:
            try:
                print_status(f"Installing {package}...")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '--upgrade', package
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print_success(f"✓ Successfully installed {package}")
                else:
                    print_error(f"Failed to install {package}: {result.stderr}")
                    return False
            except Exception as e:
                print_error(f"Error installing {package}: {e}")
                return False
    
    # Check for tkinter (usually comes with Python)
    try:
        import tkinter
        print_success("✓ tkinter available")
    except ImportError:
        print_warning("tkinter not available - GUI features will be disabled")
        print("To install tkinter on Ubuntu/Debian: sudo apt install python3-tkinter")
    
    print_success("✅ All dependencies checked!")
    return True

def check_and_install_dependencies():
    """Check if dependencies are available and install if needed"""
    try:
        # Quick check for main dependencies
        import requests
        import bs4
        import pandas
        return True
    except ImportError:
        print_warning("Missing dependencies detected. Installing...")
        return install_dependencies()

def extract_url_description(url: str, timeout: int = 5) -> str:
    """
    Extract title/description from a URL endpoint
    
    Args:
        url (str): URL to fetch description from
        timeout (int): Request timeout in seconds
        
    Returns:
        str: Description/title of the URL or error message
    """
    try:
        # Validate URL format
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            return "Invalid URL format"
        
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        print_status(f"Fetching description from: {print_colored_url(url)}")
        
        # Set headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Make request with timeout
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try different methods to extract title/description
        title = None
        
        # Method 1: Page title
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        
        # Method 2: Meta description
        if not title:
            from bs4.element import Tag
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            content = meta_desc.get('content') if meta_desc and isinstance(meta_desc, Tag) else None
            if isinstance(content, str):
                title = content.strip()
        
        # Method 3: Open Graph title
        if not title:
            og_title = soup.find('meta', attrs={'property': 'og:title'})
            og_content = None
            from bs4.element import Tag
            if og_title and isinstance(og_title, Tag):
                og_content = og_title.get('content')
            if isinstance(og_content, str):
                title = og_content.strip()
        
        # Method 4: First heading
        if not title:
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text().strip()
        
        # Clean up title
        if title:
            # Remove extra whitespace and limit length
            title = ' '.join(title.split())
            if len(title) > 100:
                title = title[:97] + "..."
            return title
        else:
            return "No description found"
            
    except requests.exceptions.Timeout:
        return "Request timeout"
    except requests.exceptions.ConnectionError:
        return "Connection failed"
    except requests.exceptions.HTTPError as e:
        return f"HTTP error: {e.response.status_code}"
    except Exception as e:
        return f"Error: {str(e)[:50]}"

def detect_urls_in_text(text: str) -> List[str]:
    """
    Detect URLs in text using regex
    
    Args:
        text (str): Text to search for URLs
        
    Returns:
        List[str]: List of URLs found
    """
    if not isinstance(text, str):
        return []
    
    # URL regex pattern
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        r'|www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        r'|(?:[a-zA-Z0-9][-a-zA-Z0-9]*\.)+[a-zA-Z]{2,}(?:\/[^\s]*)?'
    )
    
    urls = url_pattern.findall(text)
    return [url.strip() for url in urls if len(url.strip()) > 3]

class DataProcessor:
    def standardize_and_validate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize columns to: Name, Discription, URL, Catagory, Access (user spelling).
        Validate URLs, remove rows with invalid URLs, and extract descriptions.
        Always sort by Name descending.
        """
        # Define standard columns (user spelling)
        std_cols = ['Name', 'Discription', 'URL', 'Catagory', 'Access']
        col_map = {c.lower(): c for c in df.columns}
        # Try to map columns by common names
        name_col = col_map.get('name') or col_map.get('tool name') or col_map.get('title')
        desc_col = col_map.get('discription') or col_map.get('description') or col_map.get('synopsis')
        url_col = col_map.get('url') or col_map.get('link') or col_map.get('website')
        cat_col = col_map.get('catagory') or col_map.get('category')
        access_col = col_map.get('access') or col_map.get('access level')
        # Build new DataFrame with correct columns and order
        new_df = pd.DataFrame()
        new_df['Name'] = df[name_col] if name_col else ''
        new_df['Discription'] = df[desc_col] if desc_col else ''
        new_df['URL'] = df[url_col] if url_col else ''
        new_df['Catagory'] = df[cat_col] if cat_col else ''
        new_df['Access'] = df[access_col] if access_col else ''
        # Validate URLs and extract descriptions
        valid_rows = []
        for idx, row in new_df.iterrows():
            url = str(row['URL']).strip()
            name = str(row['Name']).strip()
            if not url:
                continue
            # Validate URL exists
            try:
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                resp = requests.head(url, allow_redirects=True, timeout=5)
                if resp.status_code >= 400:
                    continue
            except Exception:
                continue
            # Always extract description from URL and set in Discription
            description = extract_url_description(url)
            new_df.at[idx, 'Discription'] = description
            new_df.at[idx, 'URL'] = url
            new_df.at[idx, 'Name'] = name
            print_success(f"📝 {url} → {description}")
            valid_rows.append(idx)
        # Keep only valid rows
        new_df = new_df.loc[valid_rows].reset_index(drop=True)
        # Remove rows where Discription contains 401, 402, 403, or 404 (as substring, case-insensitive)
        mask = ~new_df['Discription'].astype(str).str.contains(r'\b(401|402|403|404)\b', case=False, na=False)
        new_df = new_df[mask].reset_index(drop=True)
        # Sort by Name descending
        new_df = new_df.sort_values(by='Name', ascending=False, key=lambda x: x.astype(str).str.lower()).reset_index(drop=True)
        return new_df
    """Handles data import and processing with alphabetical sorting and URL description extraction"""
    
    def __init__(self):
        self.supported_formats = ['.xlsx', '.xls', '.csv']
        self.data_cache = {}
        self.url_cache = {}  # Cache URL descriptions to avoid repeated requests
    
    def process_urls_in_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process URLs in dataframe and add description columns
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            pd.DataFrame: Dataframe with URL descriptions added
        """
        try:
            df_processed = df.copy()
            url_columns_found = []
            description_col = None
            # Find columns named 'Description' and 'Synopsis' (case-insensitive)
            description_col = None
            synopsis_col = None
            for col in df_processed.columns:
                col_lower = col.strip().lower()
                if col_lower == 'description':
                    description_col = col
                elif col_lower == 'synopsis':
                    synopsis_col = col

            # Scan all columns for URLs
            for col in df.columns:
                urls_found = False
                descriptions = []
                for idx, cell_value in enumerate(df[col]):
                    if pd.isna(cell_value):
                        descriptions.append("")
                        continue
                    cell_str = str(cell_value)
                    urls = detect_urls_in_text(cell_str)
                    if urls:
                        urls_found = True
                        url = urls[0]
                        # Check cache first
                        if url in self.url_cache:
                            description = self.url_cache[url]
                        else:
                            description = extract_url_description(url)
                            self.url_cache[url] = description
                            time.sleep(0.5)
                        descriptions.append(description)
                        print_success(f"📝 {url} → {description}")
                        # If there is a Description column, fill it if empty/NaN/whitespace or is 'nan'
                        if description_col:
                            desc_val = df_processed.at[idx, description_col]
                            if pd.isna(desc_val) or str(desc_val).strip().lower() in ('', 'nan', 'none'):
                                # Prefer synopsis if available and non-empty
                                if synopsis_col:
                                    syn_val = df_processed.at[idx, synopsis_col]
                                    if not pd.isna(syn_val) and str(syn_val).strip().lower() not in ('', 'nan', 'none'):
                                        df_processed.at[idx, description_col] = str(syn_val).strip()
                                    else:
                                        df_processed.at[idx, description_col] = description
                                else:
                                    df_processed.at[idx, description_col] = description
                    else:
                        descriptions.append("")
                # Add description column if URLs were found
                if urls_found:
                    desc_col_name = f"{col}_Description"
                    df_processed[desc_col_name] = descriptions
                    url_columns_found.append(col)
                    print_status(f"Added descriptions for URLs in column '{col}'")
            if url_columns_found:
                print_success(f"✅ Processed URLs in {len(url_columns_found)} columns: {', '.join(url_columns_found)}")
            else:
                print_status("No URLs detected in the data")
            return df_processed
        except Exception as e:
            print_error(f"Failed to process URLs: {e}")
            return df
    
    def import_data_file(self, file_path: str, sort_column: Optional[str] = None, 
                        sort_ascending: bool = True, export_consolidated_csv: bool = True) -> Optional[pd.DataFrame]:
        """
        Import data from XLS, XLSX, or CSV file with automatic alphabetical sorting
        
        Args:
            file_path (str): Path to the data file
            sort_column (str, optional): Column to sort by. If None, sorts by first column
            sort_ascending (bool): Sort in ascending order (A-Z) if True, descending (Z-A) if False
            export_consolidated_csv (bool): If True, export consolidated data to CSV
            
        Returns:
            pd.DataFrame: Sorted dataframe or None if import failed
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                print_error(f"File not found: {file_path}")
                return None
            file_ext = file_path_obj.suffix.lower()
            if file_ext not in self.supported_formats:
                print_error(f"Unsupported file format: {file_ext}")
                print(f"Supported formats: {', '.join(self.supported_formats)}")
                return None
            
            print_status(f"Importing data from: {print_colored_url(str(file_path_obj))}")

            # Import and consolidate all sheets for Excel files
            if file_ext in ['.xlsx', '.xls']:
                try:
                    all_sheets = pd.read_excel(str(file_path_obj), sheet_name=None, engine='openpyxl' if file_ext == '.xlsx' else 'xlrd')
                except Exception as e:
                    print_warning(f"Primary engine failed, trying alternative: {e}")
                    all_sheets = pd.read_excel(str(file_path_obj), sheet_name=None)
                df = pd.concat(all_sheets.values(), ignore_index=True)
                print_success(f"Consolidated {len(all_sheets)} sheet(s) into a single table with {len(df)} rows.")
            elif file_ext == '.csv':
                # Check for misplaced commas by comparing number of columns in first 10 rows
                with open(str(file_path_obj), encoding='utf-8-sig') as f:
                    lines = [next(f) for _ in range(10)]
                col_counts = [len(line.split(',')) for line in lines]
                if len(set(col_counts)) > 1:
                    print_warning(f"Possible misplaced commas detected in first 10 rows: {col_counts}")
                df = pd.read_csv(str(file_path_obj), encoding='utf-8-sig')
            else:
                print_error(f"Unsupported file format: {file_ext}")
                return None

            print_success(f"Successfully imported {len(df)} rows and {len(df.columns)} columns")

            # Display column information
            print(f"{CYAN}Columns found:{NC}")
            for i, col in enumerate(df.columns):
                print(f"  {i+1}. {col}")

            # Process URLs and extract descriptions
            print_status("Scanning for URLs and extracting descriptions...")
            df = self.process_urls_in_dataframe(df)

            # Apply alphabetical sorting
            sorted_df = self.sort_dataframe_alphabetically(df, sort_column, sort_ascending)

            # Cache the data
            self.data_cache[str(file_path_obj)] = sorted_df

            # Export consolidated data to CSV if requested
            if export_consolidated_csv:
                output_csv = file_path_obj.parent / f"consolidated_{file_path_obj.stem}.csv"
                sorted_df.to_csv(str(output_csv), index=False, encoding='utf-8-sig')
                print_success(f"Consolidated data exported to {output_csv}")

            return sorted_df

        except Exception as e:
            print_error(f"Failed to import data from {file_path}: {e}")
            return None
    
    def sort_dataframe_alphabetically(self, df: pd.DataFrame, sort_column: Optional[str] = None, 
                                    ascending: bool = True, sort_columns: bool = False) -> pd.DataFrame:
        """
        Sort dataframe alphabetically by specified column or first column
        
        Args:
            df (pd.DataFrame): Input dataframe
            sort_column (str, optional): Column name to sort by
            ascending (bool): Sort order (True for A-Z, False for Z-A)
            sort_columns (bool): If True, sort column names alphabetically
            
        Returns:
            pd.DataFrame: Sorted dataframe
        """
        try:
            if df.empty:
                print_warning("Cannot sort empty dataframe")
                return df
            
            # Determine sort column
            if sort_column is None:
                sort_column = df.columns[0]
                print_status(f"No sort column specified, using first column: '{sort_column}'")
            elif sort_column not in df.columns:
                print_warning(f"Column '{sort_column}' not found, using first column: '{df.columns[0]}'")
                sort_column = df.columns[0]
            
            # Perform sorting
            print_status(f"Sorting data alphabetically by '{sort_column}' ({'A-Z' if ascending else 'Z-A'})")
            
            # Handle different data types for sorting
            if df[sort_column].dtype == 'object':
                # String sorting - case insensitive
                sorted_df = df.sort_values(by=sort_column, ascending=ascending, 
                                         key=lambda x: x.astype(str).str.lower(), 
                                         na_position='last')
            else:
                # Numeric or other types
                sorted_df = df.sort_values(by=sort_column, ascending=ascending, na_position='last')
            
            # Reset index to maintain clean row numbering
            sorted_df = sorted_df.reset_index(drop=True)

            # Optionally sort columns alphabetically
            if sort_columns:
                sorted_df = sorted_df[sorted(sorted_df.columns, reverse=not ascending)]
                print_status(f"Columns sorted {'A-Z' if ascending else 'Z-A'}")
            
            print_success(f"Data sorted by '{sort_column}' - showing first few entries:")
            self.display_data_table(sorted_df, sort_column, 5)
            
            return sorted_df
            
        except Exception as e:
            print_error(f"Failed to sort dataframe: {e}")
            return df
    
    def display_data_table(self, df: pd.DataFrame, highlight_column: Optional[str] = None, num_rows: int = 20):
        """Display data in a proper table format with sortable columns"""
        try:
            if df.empty:
                print_warning("No data to display")
                return
            
            print(f"\n{CYAN}📊 Data Table ({len(df)} total rows):{NC}")
            self._print_table_separator(df.columns)
            
            # Show column headers with numbers for sorting
            header_row = "│"
            for i, col in enumerate(df.columns):
                col_text = f" {i+1}.{col}"[:20]  # Column number + name
                header_row += f" {YELLOW}{col_text:<20}{NC} │"
            print(header_row)
            self._print_table_separator(df.columns)
            
            # Show data rows
            for i in range(min(num_rows, len(df))):
                row = "│"
                for j, col in enumerate(df.columns):
                    value = str(df.iloc[i, j])[:20]  # Truncate long values
                    if col == highlight_column:
                        row += f" {GREEN}{value:<20}{NC} │"
                    else:
                        row += f" {value:<20} │"
                print(row)
            
            self._print_table_separator(df.columns)
            
            if len(df) > num_rows:
                print(f"{CYAN}... showing {num_rows} of {len(df)} rows{NC}")
            
            print(f"\n{CYAN}💡 Available actions:{NC}")
            print(f"  {YELLOW}1-{len(df.columns)}{NC}: Sort by column number")
            print(f"  {YELLOW}s{NC}: Search data by keyword")
            print(f"  {YELLOW}a{NC}: Show all rows")
            print(f"  {YELLOW}r{NC}: Reset to original data")
            print(f"  {YELLOW}e{NC}: Export current data")
            print(f"  {YELLOW}q{NC}: Quit viewer")
            print(f"  {CYAN}Enter choice:{NC} ", end="")
            
        except Exception as e:
            print_error(f"Failed to display data table: {e}")
    
    def _print_table_separator(self, columns):
        """Print table separator line"""
        separator = "├"
        for _ in columns:
            separator += "─" * 22 + "┼"
        separator = separator[:-1] + "┤"
        print(separator)
    
    def search_data(self, df: pd.DataFrame, keyword: str) -> pd.DataFrame:
        """Search data by keyword across all columns"""
        try:
            if df.empty:
                print_warning("No data to search")
                return df
            
            keyword = keyword.lower().strip()
            if not keyword:
                print_warning("Please provide a search keyword")
                return df
            
            print_status(f"Searching for '{keyword}' in all columns...")
            
            # Search across all string columns
            mask = df.astype(str).apply(lambda x: x.str.lower().str.contains(keyword, na=False)).any(axis=1)
            filtered_df = df[mask]
            
            if len(filtered_df) > 0:
                print_success(f"Found {len(filtered_df)} rows containing '{keyword}'")
                return filtered_df
            else:
                print_warning(f"No results found for '{keyword}'")
                return pd.DataFrame()
            
        except Exception as e:
            print_error(f"Search failed: {e}")
            return df
    
    def interactive_data_viewer(self, df: pd.DataFrame) -> pd.DataFrame:
        """Interactive data viewer with sorting and search"""
        current_df = df.copy() if df is not None else pd.DataFrame()
        try:
            
            while True:
                self.display_data_table(current_df)
                
                user_input = input().strip().lower()
                print()  # Add spacing after input
                
                if user_input in ['q', 'quit', 'exit']:
                    print_success("Exiting data viewer...")
                    break
                
                elif user_input == 'a':
                    print_status("Showing all rows...")
                    self.display_data_table(current_df, num_rows=len(current_df))
                    input(f"{CYAN}Press Enter to continue...{NC}")
                
                elif user_input == 's':
                    keyword = input(f"{CYAN}Enter search keyword: {NC}").strip()
                    search_results = self.search_data(current_df, keyword)
                    if not search_results.empty:
                        current_df = search_results
                
                elif user_input == 'r':
                    current_df = df.copy()
                    print_success("Data reset to original")
                
                elif user_input == 'e':
                    filename = input(f"{CYAN}Export filename (without extension): {NC}").strip()
                    if filename:
                        output_path = f"{filename}.csv"
                        if self.export_sorted_data(current_df, output_path):
                            print_success(f"Data exported to {output_path}")
                    else:
                        print_warning("Export cancelled - no filename provided")
                
                elif user_input.isdigit():
                    col_num = int(user_input) - 1
                    if 0 <= col_num < len(df.columns):
                        sort_column = df.columns[col_num]
                        
                        print(f"{CYAN}Sort '{sort_column}' by:{NC}")
                        print(f"  {YELLOW}1{NC}: A-Z (ascending)")
                        print(f"  {YELLOW}2{NC}: Z-A (descending)")
                        
                        sort_choice = input(f"{CYAN}Enter choice (1 or 2): {NC}").strip()
                        
                        if sort_choice == '1':
                            ascending = True
                            order_text = "A-Z"
                        elif sort_choice == '2':
                            ascending = False
                            order_text = "Z-A"
                        else:
                            print_warning("Invalid sort order. Using A-Z")
                            ascending = True
                            order_text = "A-Z"
                        
                        current_df = self.sort_dataframe_alphabetically(current_df, sort_column, ascending)
                        print_success(f"Sorted by '{sort_column}' ({order_text})")
                    else:
                        print_error(f"Invalid column number. Use 1-{len(df.columns)}")
                
                else:
                    print_warning("Invalid choice. Please select from the menu options.")
            
            return current_df
            
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Viewer closed by user{NC}")
            return current_df
        except Exception as e:
            print_error(f"Interactive viewer error: {e}")
            return current_df
    
    def export_sorted_data(self, df: pd.DataFrame, output_path: str, format_type: str = 'csv') -> bool:
        """
        Export sorted dataframe to specified format
        
        Args:
            df (pd.DataFrame): Data to export
            output_path (str): Output file path
            format_type (str): Export format ('csv', 'xlsx', 'xls')
            
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            print_status(f"Exporting sorted data to: {print_colored_url(str(output_path_obj))}")
            if format_type.lower() == 'csv':
                df.to_csv(str(output_path_obj), index=False, encoding='utf-8-sig')
            elif format_type.lower() in ['xlsx', 'xls']:
                df.to_excel(str(output_path_obj), index=False, engine='openpyxl')
            else:
                print_error(f"Unsupported export format: {format_type}")
                return False
            
            print_success(f"Data exported successfully: {len(df)} rows, {len(df.columns)} columns")
            return True
            
        except Exception as e:
            print_error(f"Failed to export data: {e}")
            return False
    
    def batch_process_files(self, input_directory: str, output_directory: str, 
                          sort_column: Optional[str] = None) -> Dict[str, bool]:
        """
        Process multiple files in a directory with alphabetical sorting
        
        Args:
            input_directory (str): Directory containing input files
            output_directory (str): Directory for output files
            sort_column (str, optional): Column to sort by
            
        Returns:
            Dict[str, bool]: Processing results for each file
        """
        try:
            input_dir = Path(input_directory)
            output_dir = Path(output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            results = {}
            
            print_status(f"Batch processing files from: {print_colored_url(str(input_dir))}")
            
            # Find all supported files
            files_to_process = []
            for ext in self.supported_formats:
                files_to_process.extend(input_dir.glob(f"*{ext}"))
                files_to_process.extend(input_dir.glob(f"*{ext.upper()}"))
            
            if not files_to_process:
                print_warning(f"No supported files found in {input_dir}")
                return results
            
            print_status(f"Found {len(files_to_process)} files to process")
            
            for file_path in files_to_process:
                print(f"\n{CYAN}Processing: {file_path.name}{NC}")
                
                # Import and sort data
                df = self.import_data_file(str(file_path), sort_column)
                
                if df is not None:
                    # Generate output filename
                    output_file = output_dir / f"sorted_{file_path.stem}.csv"
                    
                    # Export sorted data
                    success = self.export_sorted_data(df, str(output_file), 'csv')
                    results[str(file_path)] = success
                    
                    if success:
                        print_success(f"✓ Processed: {file_path.name}")
                    else:
                        print_error(f"✗ Failed: {file_path.name}")
                else:
                    results[str(file_path)] = False
                    print_error(f"✗ Failed to import: {file_path.name}")
            
            # Summary
            successful = sum(results.values())
            total = len(results)
            print(f"\n{CYAN}Batch Processing Summary:{NC}")
            print(f"  Total files: {total}")
            print(f"  Successful: {GREEN}{successful}{NC}")
            print(f"  Failed: {RED}{total - successful}{NC}")
            print_colored_url(str(output_dir), "📁 Output directory")
            
            return results
            
        except Exception as e:
            print_error(f"Batch processing failed: {e}")
            return {}


class BusinessToolsManager:
    def show_data_browser(self, df: pd.DataFrame):
        """
        Show the Data Browser tab as the first window, with proper columns and sorting.
        """
        import tkinter as tk
        from tkinter import ttk
        import webbrowser
        # Standard columns (user spelling)
        std_cols = ['Name', 'Discription', 'URL', 'Catagory', 'Access']
        root = tk.Tk()
        root.title("Business Tools Data Browser")
        root.geometry("900x600")
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        # Treeview
        tree = ttk.Treeview(root, columns=std_cols, show='headings')
        for col in std_cols:
            tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(tree, c, std_cols))
            tree.column(col, width=180 if col != 'Discription' else 300, anchor=tk.W)
        # Insert data
        for _, row in df.iterrows():
            values = [row.get(col, '') for col in std_cols]
            # Color URL blue in GUI (if URL column)
            tags = []
            if values[2]:
                tags.append('urlblue')
            tree.insert('', tk.END, values=values, tags=tags)
        tree.tag_configure('urlblue', foreground='#1565c0')
        tree.pack(fill=tk.BOTH, expand=True)
        # Make URLs clickable
        def on_tree_click(event):
            item = tree.identify_row(event.y)
            col = tree.identify_column(event.x)
            if not item or not col:
                return
            col_idx = int(col.replace('#','')) - 1
            if std_cols[col_idx] == 'URL':
                url = tree.item(item)['values'][col_idx]
                if url:
                    webbrowser.open(url)
        tree.bind('<Button-1>', on_tree_click)
        # Add sort indicator
        self._treeview_sort_state = {'col': 'Name', 'desc': True}
        root.mainloop()

    def sort_treeview(self, tree, col, std_cols):
        # Get all items and sort
        items = [(tree.set(k, col), k) for k in tree.get_children('')]
        desc = not getattr(self, '_treeview_sort_state', {}).get('desc', True)
        items.sort(reverse=desc, key=lambda t: str(t[0]).lower())
        for idx, (_, k) in enumerate(items):
            tree.move(k, '', idx)
        self._treeview_sort_state = {'col': col, 'desc': desc}
    """Main business tools management class"""
    
    def __init__(self):
        self.app_dir = Path(__file__).parent
        self.data_processor = DataProcessor()
        self.tools_config = {
            'data_processing': {
                'name': 'Data Processing Tools',
                'url': 'https://github.com/your-org/business-tools-browser',
                'local_path': self.app_dir / 'src' / 'business_tools_app.py',
                'description': 'Excel/CSV processing with alphabetical sorting and link validation'
            },
            'red_hat_tools': {
                'name': 'Red Hat Business Tools',
                'url': f'https://access.{COMPANY_DOMAIN}/documentation',
                'local_path': self.app_dir / 'red_hat_tools.py',
                'description': 'Red Hat specific business and administrative tools'
            },
            'github_integration': {
                'name': 'GitHub Business Integration',
                'url': 'https://docs.github.com/en/enterprise',
                'local_path': self.app_dir / 'github_tools.py',
                'description': 'GitHub project and repository management tools'
            },
            'automation_suite': {
                'name': 'Business Automation Suite',
                'url': f'https://automation.{COMPANY_DOMAIN}/tools',
                'local_path': self.app_dir / 'automation_tools.py',
                'description': 'Automated business process management tools'
            }
        }
    
    def display_welcome(self):
        """Display welcome message with colored URLs"""
        print("=" * 60)
        print(f"{GREEN}🚀 Business Tools Manager{NC}")
        print("=" * 60)
        print()
        print("📊 Available Business Tools:")
        print()
        
        for tool_id, config in self.tools_config.items():
            print(f"  - {config['name']}")
            print(f"    📁 {config['description']}")
            print_colored_url(config['url'], "    🌐 Documentation")
            if config['local_path'].exists():
                print(f"    ✅ {GREEN}Available locally{NC}")
            else:
                print(f"    ❌ {YELLOW}Not installed{NC}")
            print()
    
    def launch_tool(self, tool_id):
        """Launch a specific business tool"""
        if tool_id not in self.tools_config:
            print_error(f"Unknown tool: {tool_id}")
            return False
        
        config = self.tools_config[tool_id]
        print_status(f"Launching {config['name']}...")
        
        if config['local_path'].exists():
            try:
                # Launch local tool
                result = subprocess.run([sys.executable, str(config['local_path'])], 
                                      capture_output=False)
                if result.returncode == 0:
                    print_success(f"{config['name']} completed successfully")
                else:
                    print_warning(f"{config['name']} exited with code {result.returncode}")
                return True
            except Exception as e:
                print_error(f"Failed to launch {config['name']}: {e}")
                return False
        else:
            print_warning(f"{config['name']} not installed locally")
            print_colored_url(config['url'], "🌐 Online documentation available at")
            
            # Ask if user wants to open documentation
            response = input(f"\n{CYAN}Open documentation in browser? (y/N): {NC}")
            if response.lower() in ['y', 'yes']:
                webbrowser.open(config['url'])
                print_success("Documentation opened in browser")
            return False
    
    def show_gui(self):
        """Show main GUI interface for business tools, with a dashboard/welcome window."""
        import tkinter as tk
        from tkinter import filedialog, messagebox
        root = tk.Tk()
        root.title("Business Tools Browser")
        root.geometry("500x350")
        # Welcome label
        welcome = tk.Label(root, text="Business Tools Browser", font=("Arial", 18, "bold"), pady=20)
        welcome.pack()
        # Description
        desc = tk.Label(root, text="Welcome! Select an option below:", font=("Arial", 12))
        desc.pack(pady=10)
        # Open Data Browser button
        def open_data_browser():
            file_path = filedialog.askopenfilename(title="Select Data File", filetypes=[("Excel/CSV Files", "*.csv *.xlsx *.xls")])
            if not file_path:
                return
            df = self.data_processor.import_data_file(file_path, sort_column='Name', sort_ascending=False)
            if df is not None:
                df_std = self.data_processor.standardize_and_validate_dataframe(df)
                root.withdraw()
                self.show_data_browser(df_std)
                root.deiconify()
            else:
                messagebox.showerror("Error", "Failed to load data file.")
        btn_data_browser = tk.Button(root, text="Open Data Browser", font=("Arial", 13), width=22, command=open_data_browser)
        btn_data_browser.pack(pady=18)
        # Exit button
        btn_exit = tk.Button(root, text="Exit", font=("Arial", 13), width=22, command=root.destroy)
        btn_exit.pack(pady=5)
        # About/info
        info = tk.Label(root, text="© 2025 Business Tools Browser", font=("Arial", 9), fg="#888")
        info.pack(side=tk.BOTTOM, pady=10)
        root.mainloop()
    
    def process_data_file(self, file_path: str, sort_column: Optional[str] = None, 
                         output_path: Optional[str] = None, sort_order: str = 'asc', 
                         interactive: bool = False) -> bool:
        """
        Process a single data file with alphabetical sorting and optional interactive viewer
        
        Args:
            file_path (str): Path to input file
            sort_column (str, optional): Column to sort by
            output_path (str, optional): Path for output file
            sort_order (str): 'asc' for A-Z, 'desc' for Z-A
            interactive (bool): Launch interactive viewer
            
        Returns:
            bool: True if processing successful
        """
        try:
            print_status(f"Processing data file: {print_colored_url(file_path)}")
            
            # Import and sort data
            ascending = sort_order.lower() in ['asc', 'ascending', 'a-z']
            df = self.data_processor.import_data_file(file_path, sort_column, ascending)
            
            if df is None:
                return False
            
            # Launch interactive viewer if requested
            if interactive:
                print(f"\n{GREEN}🔍 Launching Interactive Data Viewer{NC}")
                print("You can sort columns, search data, and export results!")
                final_df = self.data_processor.interactive_data_viewer(df)
                
                # Ask if user wants to save the final state
                save_choice = input(f"\n{CYAN}Save current data state? (y/N): {NC}").strip().lower()
                if save_choice in ['y', 'yes']:
                    df = final_df
            
            # Determine output path
            if output_path is None:
                input_path = Path(file_path)
                output_path = str(input_path.parent / f"sorted_{input_path.stem}.csv")
            
            # Export sorted data
            success = self.data_processor.export_sorted_data(df, str(output_path), 'csv')
            
            if success:
                print_success("Data processing completed successfully!")
                print_colored_url(str(output_path), "📄 Output file")
            
            return success
            
        except Exception as e:
            print_error(f"Data processing failed: {e}")
            return False
    
    def install_tool(self, tool_id):
        """Install a business tool"""
        if tool_id not in self.tools_config:
            print_error(f"Unknown tool: {tool_id}")
            return False
        
        config = self.tools_config[tool_id]
        print_status(f"Installing {config['name']}...")
        print_colored_url(config['url'], "📥 Downloading from")
        
        # Placeholder for actual installation logic
        print_warning("Installation feature coming soon!")
        print("For now, please refer to the documentation:")
        print_colored_url(config['url'])
        return False
    
    def batch_process_directory(self, directory_path: str, file_pattern: str = "*.{csv,xlsx,xls}",
                               sort_column: Optional[str] = None, output_dir: Optional[str] = None) -> bool:
        """
        Batch process all data files in a directory
        
        Args:
            directory_path (str): Directory containing data files
            file_pattern (str): File pattern to match (default: CSV and Excel files)
            sort_column (str, optional): Column to sort by
            output_dir (str, optional): Output directory for processed files
            
        Returns:
            bool: True if batch processing successful
        """
        try:
            print_status(f"Starting batch processing in: {print_colored_url(directory_path)}")
            
            dir_path = Path(directory_path)
            if not dir_path.exists():
                print_error(f"Directory not found: {directory_path}")
                return False
            
            # Find matching files
            file_patterns = ['*.csv', '*.xlsx', '*.xls']
            files_to_process = []
            
            for pattern in file_patterns:
                files_to_process.extend(dir_path.glob(pattern))
            
            if not files_to_process:
                print_error("No data files found in the specified directory")
                return False
            
            # Process each file
            success_count = 0
            for file_path in files_to_process:
                output_path = None
                if output_dir:
                    output_dir_path = Path(output_dir)
                    output_dir_path.mkdir(exist_ok=True)
                    output_path = output_dir_path / f"sorted_{file_path.stem}.csv"
                
                if self.process_data_file(str(file_path), sort_column, 
                                        str(output_path) if output_path else None):
                    success_count += 1
            
            print_success(f"Batch processing completed! {success_count}/{len(files_to_process)} files processed successfully")
            return success_count > 0
            
        except Exception as e:
            print_error(f"Batch processing failed: {e}")
            return False

def show_help():
    """Display help information with colored URLs"""
    print(f"\n{GREEN}🚀 Business Tools Manager - Help{NC}")
    print("=" * 50)
    print(f"\n{CYAN}USAGE:{NC}")
    print(f"  python3 business_tools.py [command] [options]")
    
    print(f"\n{CYAN}COMMANDS:{NC}")
    print(f"  {YELLOW}gui{NC}                    Launch GUI interface")
    print(f"  {YELLOW}view <file>{NC}            Interactive data viewer with URL extraction")
    print(f"  {YELLOW}process <file>{NC}         Process data file with alphabetical sorting")
    print(f"  {YELLOW}batch <directory>{NC}      Batch process directory")
    print(f"  {YELLOW}list{NC}                   List available business tools")
    print(f"  {YELLOW}deps{NC}                   Install/check dependencies")
    print(f"  {YELLOW}help{NC}                   Show this help")
    
    print(f"\n{CYAN}EXAMPLES:{NC}")
    print(f"  {CYAN}python3 business_tools.py view data.xlsx{NC}")
    print(f"  {CYAN}python3 business_tools.py process Red_Hat_Tools.xlsx{NC}")
    print(f"  {CYAN}python3 business_tools.py batch /path/to/data/folder{NC}")
    print(f"  {CYAN}python3 business_tools.py deps{NC}")
    
    print(f"\n{CYAN}FEATURES:{NC}")
    print(f"  - Multi-format support: XLS, XLSX, CSV")
    print(f"  - Automatic URL detection and description extraction")
    print(f"  - Interactive table viewer with sorting and search")
    print(f"  - Alphabetical data sorting (A-Z, Z-A)")
    print(f"  - Batch processing with progress tracking")
    print(f"  - Automatic dependency installation")
    
    print(f"\n{CYAN}URL EXTRACTION:{NC}")
    print(f"  When importing files with URLs, the tool automatically:")
    print(f"  - Detects URLs in any column")
    print(f"  - Fetches page titles/descriptions from each URL")
    print(f"  - Adds new columns with extracted descriptions")
    print(f"  - Caches results to avoid duplicate requests")
    
    print(f"\n{CYAN}DOCUMENTATION:{NC}")
    print_colored_url("https://github.com/your-org/business-tools", "🌐 Project Repository")
    print_colored_url(f"https://docs.{COMPANY_DOMAIN}/business-tools", "📚 Enterprise Documentation")
    print()

def main():
    """Main application entry point"""
    try:
        # Check and install dependencies first
        if not check_and_install_dependencies():
            print_error("Failed to install required dependencies")
            sys.exit(1)
        
        manager = BusinessToolsManager()
        
        if len(sys.argv) == 1:
            # No arguments - launch GUI
            manager.display_welcome()
            print()
            print(f"{CYAN}Launching GUI interface...{NC}")
            manager.show_gui()
        elif len(sys.argv) >= 2:
            command = sys.argv[1].lower()
            if command in ['--cli', 'cli']:
                # CLI mode: interactive data viewer
                manager.display_welcome()
                print()
                print(f"{CYAN}Launching CLI Interactive Data Viewer...{NC}")
                # Ask user for file
                file_path = None
                if len(sys.argv) >= 3:
                    file_path = sys.argv[2]
                while not file_path:
                    file_path = input(f"{CYAN}Enter path to data file (csv/xlsx/xls): {NC}").strip()
                    if not file_path:
                        print_warning("No file specified. Please enter a file path.")
                df = manager.data_processor.import_data_file(file_path, sort_column='Name', sort_ascending=False)
                if df is not None:
                    df_std = manager.data_processor.standardize_and_validate_dataframe(df)
                    manager.data_processor.interactive_data_viewer(df_std)
                else:
                    print_error("Failed to load data file.")
            elif command in ['help', '-h', '--help']:
                show_help()
            elif command == 'gui':
                manager.show_gui()
            elif command == 'list':
                manager.display_welcome()
            elif command == 'view':
                if len(sys.argv) >= 3:
                    file_path = sys.argv[2]
                    print_status("🔍 Launching Interactive Data Viewer with URL extraction...")
                    success = manager.process_data_file(file_path, interactive=True)
                    if success:
                        print_success("✅ Data viewing session completed!")
                    else:
                        print_error("❌ Failed to load data file")
                        sys.exit(1)
                else:
                    print_error("Please specify a file path to view")
                    print(f"{CYAN}Usage: python3 business_tools.py view <file_path>{NC}")
            elif command == 'process':
                if len(sys.argv) >= 3:
                    file_path = sys.argv[2]
                    sort_column = sys.argv[3] if len(sys.argv) >= 4 else None
                    output_path = sys.argv[4] if len(sys.argv) >= 5 else None
                    print_status("📊 Starting data processing with URL extraction and alphabetical sorting...")
                    success = manager.process_data_file(file_path, sort_column, output_path)
                    if success:
                        print_success("✅ Data processing completed successfully!")
                    else:
                        print_error("❌ Data processing failed")
                        sys.exit(1)
                else:
                    print_error("Please specify a file path to process")
                    print(f"{CYAN}Usage: python3 business_tools.py process <file_path> [sort_column] [output_path]{NC}")
            elif command == 'batch':
                if len(sys.argv) >= 3:
                    directory_path = sys.argv[2]
                    sort_column = sys.argv[3] if len(sys.argv) >= 4 else None
                    output_dir = sys.argv[4] if len(sys.argv) >= 5 else None
                    print_status("📁 Starting batch processing with URL extraction and alphabetical sorting...")
                    success = manager.batch_process_directory(directory_path, sort_column=sort_column, output_dir=output_dir)
                    if success:
                        print_success("✅ Batch processing completed successfully!")
                    else:
                        print_error("❌ Batch processing failed")
                        sys.exit(1)
                else:
                    print_error("Please specify a directory path to process")
                    print(f"{CYAN}Usage: python3 business_tools.py batch <directory_path> [sort_column] [output_dir]{NC}")
            elif command == 'deps':
                print_status("🔧 Manually checking and installing dependencies...")
                if install_dependencies():
                    print_success("✅ All dependencies are ready!")
                else:
                    print_error("❌ Dependency installation failed")
                    sys.exit(1)
            else:
                print_error(f"Unknown command: {command}")
                print(f"{CYAN}Use 'python3 business_tools.py help' for usage information{NC}")
        
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Operation cancelled by user{NC}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
