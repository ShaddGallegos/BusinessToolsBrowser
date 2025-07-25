#!/usr/bin/env python3
"""
Enhanced Business Tools Browser
Handles multiple file types, link validation, data formatting, and master CSV creation
"""

import argparse
import csv
import json
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import pandas as pd
import requests
from urllib.parse import urlparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue

# Application directories
APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data"
RESOURCES_DIR = APP_DIR / "resources"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
RESOURCES_DIR.mkdir(exist_ok=True)

class LinkValidator:
    """Validates URLs and checks their accessibility"""
    
    def __init__(self, timeout=10, max_workers=20):
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Business Tools Browser) Link Validator/1.0'
        })
    
    def validate_url(self, url):
        """Validate a single URL"""
        if not url or pd.isna(url) or str(url).strip() == '':
            return {'url': url, 'status': 'empty', 'code': None, 'message': 'Empty URL'}
        
        url = str(url).strip()
        if not url.startswith(('http://', 'https://')):
            if url.startswith('www.'):
                url = 'https://' + url
            elif '.' in url:
                url = 'https://' + url
            else:
                return {'url': url, 'status': 'invalid', 'code': None, 'message': 'Invalid URL format'}
        
        try:
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            if response.status_code == 405:  # Method Not Allowed, try GET
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            
            if response.status_code < 400:
                return {'url': url, 'status': 'valid', 'code': response.status_code, 'message': 'OK'}
            else:
                return {'url': url, 'status': 'error', 'code': response.status_code, 'message': f'HTTP {response.status_code}'}
        
        except requests.exceptions.Timeout:
            return {'url': url, 'status': 'timeout', 'code': None, 'message': 'Timeout'}
        except requests.exceptions.ConnectionError:
            return {'url': url, 'status': 'connection_error', 'code': None, 'message': 'Connection failed'}
        except requests.exceptions.RequestException as e:
            return {'url': url, 'status': 'error', 'code': None, 'message': str(e)}
        except Exception as e:
            return {'url': url, 'status': 'error', 'code': None, 'message': f'Unexpected error: {str(e)}'}
    
    def validate_urls_batch(self, urls, progress_callback=None):
        """Validate multiple URLs with progress tracking"""
        results = []
        total = len(urls)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.validate_url, url): url for url in urls}
            
            for i, future in enumerate(as_completed(future_to_url)):
                result = future.result()
                results.append(result)
                
                if progress_callback:
                    progress_callback(i + 1, total, result)
        
        return results

class DataProcessor:
    """Enhanced data processor for multiple file types"""
    
    def __init__(self):
        self.master_csv = DATA_DIR / "Master_Tools.csv"
        self.validation_report = DATA_DIR / "Link_Validation_Report.csv"
        self.supported_formats = ['.xlsx', '.xls', '.csv']
        self.link_validator = LinkValidator()
        
        # Standard column mappings
        self.column_mappings = {
            'name': ['name', 'tool_name', 'tool', 'title', 'application', 'service'],
            'description': ['description', 'desc', 'summary', 'overview', 'about'],
            'url': ['url', 'link', 'website', 'web_address', 'site'],
            'category': ['category', 'type', 'classification', 'group'],
            'access': ['access', 'availability', 'access_type', 'public', 'internal'],
            'notes': ['notes', 'comments', 'remarks', 'additional_info']
        }
    
    def detect_file_format(self, file_path):
        """Detect and validate file format"""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        suffix = file_path.suffix.lower()
        if suffix not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {suffix}. Supported: {', '.join(self.supported_formats)}")
        
        return suffix
    
    def read_file(self, file_path):
        """Read file based on its format"""
        file_format = self.detect_file_format(file_path)
        
        try:
            if file_format in ['.xlsx', '.xls']:
                # Try to read Excel file, handle multiple sheets
                df = pd.read_excel(file_path, sheet_name=None)
                if isinstance(df, dict):
                    # Multiple sheets - combine them
                    combined_df = pd.DataFrame()
                    for sheet_name, sheet_df in df.items():
                        sheet_df['source_sheet'] = sheet_name
                        combined_df = pd.concat([combined_df, sheet_df], ignore_index=True)
                    return combined_df
                else:
                    return df
            
            elif file_format == '.csv':
                return pd.read_csv(file_path, encoding='utf-8')
        
        except Exception as e:
            # Try different encodings for CSV
            if file_format == '.csv':
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        return pd.read_csv(file_path, encoding=encoding)
                    except:
                        continue
            raise Exception(f"Failed to read file {file_path}: {str(e)}")
    
    def standardize_columns(self, df):
        """Standardize column names based on mappings"""
        df_copy = df.copy()
        
        # Create a mapping of current columns to standard names
        column_map = {}
        current_columns = [col.lower().strip() for col in df_copy.columns]
        
        for standard_col, variations in self.column_mappings.items():
            for variation in variations:
                if variation.lower() in current_columns:
                    original_col = df_copy.columns[current_columns.index(variation.lower())]
                    column_map[original_col] = standard_col
                    break
        
        # Rename columns
        df_copy = df_copy.rename(columns=column_map)
        
        # Ensure all standard columns exist
        for standard_col in self.column_mappings.keys():
            if standard_col not in df_copy.columns:
                df_copy[standard_col] = ''
        
        # Add metadata columns
        df_copy['source_file'] = ''
        df_copy['date_processed'] = pd.Timestamp.now().isoformat()
        df_copy['link_status'] = ''
        df_copy['link_code'] = ''
        df_copy['link_message'] = ''
        
        return df_copy
    
    def classify_tool_access(self, row):
        """Enhanced tool classification"""
        url = str(row.get('url', '')).lower()
        description = str(row.get('description', '')).lower()
        name = str(row.get('name', '')).lower()
        
        # Internal indicators
        internal_keywords = ['internal', 'intranet', 'private', 'corp', 'company', 'localhost', '192.168', '10.0', '172.16']
        # Public indicators
        public_keywords = ['public', 'open', 'free', 'community', 'github', 'google', 'microsoft']
        
        # Check URL for internal indicators
        for keyword in internal_keywords:
            if keyword in url or keyword in description or keyword in name:
                return 'Internal'
        
        # Check for public indicators
        for keyword in public_keywords:
            if keyword in url or keyword in description or keyword in name:
                return 'Public'
        
        # Default classification based on URL
        if any(domain in url for domain in ['.com', '.org', '.net', '.gov', '.edu']):
            return 'Public'
        
        return 'Unknown'
    
    def validate_links_with_progress(self, df, progress_callback=None):
        """Validate all links in the dataframe with progress tracking"""
        if 'url' not in df.columns:
            return df
        
        urls = df['url'].tolist()
        
        def update_progress(current, total, result):
            if progress_callback:
                progress_callback(f"Validating links: {current}/{total} - {result['status']}")
        
        validation_results = self.link_validator.validate_urls_batch(urls, update_progress)
        
        # Update dataframe with validation results
        for i, result in enumerate(validation_results):
            df.loc[i, 'link_status'] = result['status']
            df.loc[i, 'link_code'] = result['code'] if result['code'] else ''
            df.loc[i, 'link_message'] = result['message']
        
        return df
    
    def process_files(self, file_paths, progress_callback=None):
        """Process multiple files and create master CSV"""
        all_data = []
        
        for i, file_path in enumerate(file_paths):
            if progress_callback:
                progress_callback(f"Processing file {i+1}/{len(file_paths)}: {Path(file_path).name}")
            
            try:
                # Read and standardize file
                df = self.read_file(file_path)
                df = self.standardize_columns(df)
                df['source_file'] = str(Path(file_path).name)
                
                # Classify access types
                df['access'] = df.apply(self.classify_tool_access, axis=1)
                
                all_data.append(df)
                
            except Exception as e:
                if progress_callback:
                    progress_callback(f"Error processing {file_path}: {str(e)}")
                continue
        
        if not all_data:
            raise Exception("No files were successfully processed")
        
        # Combine all data
        if progress_callback:
            progress_callback("Combining data from all files...")
        
        master_df = pd.concat(all_data, ignore_index=True)
        
        # Remove duplicates based on URL
        if progress_callback:
            progress_callback("Removing duplicate entries...")
        
        master_df = master_df.drop_duplicates(subset=['url'], keep='first')
        
        # Validate links
        if progress_callback:
            progress_callback("Starting link validation...")
        
        master_df = self.validate_links_with_progress(master_df, progress_callback)
        
        # Save master CSV
        if progress_callback:
            progress_callback("Saving master CSV...")
        
        master_df.to_csv(self.master_csv, index=False)
        
        # Create validation report
        validation_df = master_df[['name', 'url', 'link_status', 'link_code', 'link_message', 'source_file']].copy()
        validation_df.to_csv(self.validation_report, index=False)
        
        if progress_callback:
            progress_callback(f"Processing complete! Master CSV saved with {len(master_df)} entries.")
        
        return master_df, len(all_data)

class BusinessToolsGUI:
    """Enhanced GUI for the Business Tools Browser"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Business Tools Browser - Enhanced")
        self.root.geometry("1200x800")
        
        self.processor = DataProcessor()
        self.current_data = None
        
        self.setup_gui()
        self.load_existing_data()
    
    def setup_gui(self):
        """Setup the GUI interface"""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: File Processing
        self.processing_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.processing_frame, text="File Processing")
        self.setup_processing_tab()
        
        # Tab 2: Data Browser
        self.browser_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.browser_frame, text="Data Browser")
        self.setup_browser_tab()
        
        # Tab 3: Link Validation
        self.validation_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.validation_frame, text="Link Validation")
        self.setup_validation_tab()
    
    def setup_processing_tab(self):
        """Setup file processing tab"""
        # File selection frame
        file_frame = ttk.LabelFrame(self.processing_frame, text="File Selection", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(file_frame, text="Select Files (XLS/XLSX/CSV)", 
                  command=self.select_files).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(file_frame, text="Process Selected Files", 
                  command=self.process_files).pack(side=tk.LEFT, padx=5)
        
        # Selected files list
        list_frame = ttk.LabelFrame(self.processing_frame, text="Selected Files", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.files_listbox = tk.Listbox(list_frame, height=8)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.files_listbox.yview)
        self.files_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(self.processing_frame, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_var = tk.StringVar(value="Ready to process files...")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.selected_files = []
    
    def setup_browser_tab(self):
        """Setup data browser tab"""
        # Controls frame
        controls_frame = ttk.Frame(self.browser_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Refresh Data", 
                  command=self.load_existing_data).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(controls_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar()
        self.filter_entry = ttk.Entry(controls_frame, textvariable=self.filter_var)
        self.filter_entry.pack(side=tk.LEFT, padx=5)
        self.filter_entry.bind('<KeyRelease>', self.apply_filter)
        
        # Data display
        data_frame = ttk.Frame(self.browser_frame)
        data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for data display
        columns = ['Name', 'Description', 'URL', 'Category', 'Access', 'Link Status', 'Source File']
        self.tree = ttk.Treeview(data_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.W)
            self.tree.column(col, width=150, anchor=tk.W)
        
        # Scrollbars for treeview
        v_scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(data_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        data_frame.grid_rowconfigure(0, weight=1)
        data_frame.grid_columnconfigure(0, weight=1)
        
        # Double-click to open URL
        self.tree.bind('<Double-1>', self.open_url)
    
    def setup_validation_tab(self):
        """Setup link validation tab"""
        # Controls
        controls_frame = ttk.Frame(self.validation_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Re-validate All Links", 
                  command=self.revalidate_links).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls_frame, text="Export Validation Report", 
                  command=self.export_validation_report).pack(side=tk.LEFT, padx=5)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(self.validation_frame, text="Link Validation Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=6, width=80)
        self.stats_text.pack(fill=tk.X)
        
        # Validation results
        results_frame = ttk.LabelFrame(self.validation_frame, text="Validation Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        val_columns = ['Name', 'URL', 'Status', 'Code', 'Message', 'Source File']
        self.val_tree = ttk.Treeview(results_frame, columns=val_columns, show='headings', height=15)
        
        for col in val_columns:
            self.val_tree.heading(col, text=col, anchor=tk.W)
            self.val_tree.column(col, width=120, anchor=tk.W)
        
        val_v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.val_tree.yview)
        val_h_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.val_tree.xview)
        self.val_tree.configure(yscrollcommand=val_v_scrollbar.set, xscrollcommand=val_h_scrollbar.set)
        
        self.val_tree.grid(row=0, column=0, sticky='nsew')
        val_v_scrollbar.grid(row=0, column=1, sticky='ns')
        val_h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
    
    def select_files(self):
        """Select multiple files for processing"""
        files = filedialog.askopenfilenames(
            title="Select Data Files",
            filetypes=[
                ("All Supported", "*.xlsx *.xls *.csv"),
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if files:
            self.selected_files = list(files)
            self.update_files_list()
    
    def update_files_list(self):
        """Update the files listbox"""
        self.files_listbox.delete(0, tk.END)
        for file_path in self.selected_files:
            self.files_listbox.insert(tk.END, Path(file_path).name)
    
    def update_progress(self, message):
        """Update progress display"""
        self.progress_var.set(message)
        self.root.update()
    
    def process_files(self):
        """Process selected files in background thread"""
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select files to process first.")
            return
        
        def process_thread():
            try:
                self.progress_bar.start()
                self.update_progress("Starting file processing...")
                
                master_df, file_count = self.processor.process_files(
                    self.selected_files, 
                    self.update_progress
                )
                
                self.progress_bar.stop()
                self.update_progress(f"Completed! Processed {file_count} files, {len(master_df)} total entries.")
                
                # Load the new data
                self.load_existing_data()
                
                messagebox.showinfo("Success", 
                    f"Successfully processed {file_count} files!\n"
                    f"Total entries: {len(master_df)}\n"
                    f"Master CSV saved to: {self.processor.master_csv}")
                
            except Exception as e:
                self.progress_bar.stop()
                self.update_progress(f"Error: {str(e)}")
                messagebox.showerror("Error", f"Processing failed: {str(e)}")
        
        threading.Thread(target=process_thread, daemon=True).start()
    
    def load_existing_data(self):
        """Load existing master CSV data"""
        if self.processor.master_csv.exists():
            try:
                self.current_data = pd.read_csv(self.processor.master_csv)
                self.populate_tree()
                self.populate_validation_tree()
                self.update_validation_stats()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def populate_tree(self):
        """Populate the main data tree"""
        if self.current_data is None:
            return
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add data rows
        for _, row in self.current_data.iterrows():
            values = [
                row.get('name', ''),
                row.get('description', '')[:50] + '...' if len(str(row.get('description', ''))) > 50 else row.get('description', ''),
                row.get('url', ''),
                row.get('category', ''),
                row.get('access', ''),
                row.get('link_status', ''),
                row.get('source_file', '')
            ]
            self.tree.insert('', 'end', values=values)
    
    def populate_validation_tree(self):
        """Populate the validation results tree"""
        if self.current_data is None:
            return
        
        # Clear existing data
        for item in self.val_tree.get_children():
            self.val_tree.delete(item)
        
        # Add validation data
        for _, row in self.current_data.iterrows():
            values = [
                row.get('name', ''),
                row.get('url', ''),
                row.get('link_status', ''),
                row.get('link_code', ''),
                row.get('link_message', ''),
                row.get('source_file', '')
            ]
            self.val_tree.insert('', 'end', values=values)
    
    def update_validation_stats(self):
        """Update validation statistics"""
        if self.current_data is None:
            return
        
        stats = self.current_data['link_status'].value_counts()
        total = len(self.current_data)
        
        stats_text = f"Link Validation Statistics:\n"
        stats_text += f"Total entries: {total}\n\n"
        
        for status, count in stats.items():
            percentage = (count / total) * 100
            stats_text += f"{status.title()}: {count} ({percentage:.1f}%)\n"
        
        self.stats_text.delete('1.0', tk.END)
        self.stats_text.insert('1.0', stats_text)
    
    def apply_filter(self, event=None):
        """Apply filter to the data display"""
        if self.current_data is None:
            return
        
        filter_text = self.filter_var.get().lower()
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter and populate
        if filter_text:
            filtered_data = self.current_data[
                self.current_data.apply(
                    lambda row: filter_text in str(row.get('name', '')).lower() or
                               filter_text in str(row.get('description', '')).lower() or
                               filter_text in str(row.get('category', '')).lower() or
                               filter_text in str(row.get('url', '')).lower(),
                    axis=1
                )
            ]
        else:
            filtered_data = self.current_data
        
        for _, row in filtered_data.iterrows():
            values = [
                row.get('name', ''),
                row.get('description', '')[:50] + '...' if len(str(row.get('description', ''))) > 50 else row.get('description', ''),
                row.get('url', ''),
                row.get('category', ''),
                row.get('access', ''),
                row.get('link_status', ''),
                row.get('source_file', '')
            ]
            self.tree.insert('', 'end', values=values)
    
    def open_url(self, event):
        """Open URL in browser when double-clicked"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            url = item['values'][2]  # URL is the 3rd column
            if url:
                import webbrowser
                webbrowser.open(url)
    
    def revalidate_links(self):
        """Re-validate all links"""
        if self.current_data is None:
            messagebox.showwarning("No Data", "No data loaded. Please process files first.")
            return
        
        def revalidate_thread():
            try:
                self.progress_bar.start()
                self.update_progress("Re-validating all links...")
                
                self.current_data = self.processor.validate_links_with_progress(
                    self.current_data, 
                    self.update_progress
                )
                
                # Save updated data
                self.current_data.to_csv(self.processor.master_csv, index=False)
                
                self.progress_bar.stop()
                self.update_progress("Link validation completed!")
                
                # Refresh displays
                self.populate_tree()
                self.populate_validation_tree()
                self.update_validation_stats()
                
                messagebox.showinfo("Success", "Link validation completed!")
                
            except Exception as e:
                self.progress_bar.stop()
                self.update_progress(f"Error: {str(e)}")
                messagebox.showerror("Error", f"Validation failed: {str(e)}")
        
        threading.Thread(target=revalidate_thread, daemon=True).start()
    
    def export_validation_report(self):
        """Export validation report"""
        if self.current_data is None:
            messagebox.showwarning("No Data", "No data loaded.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Validation Report",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                validation_df = self.current_data[['name', 'url', 'link_status', 'link_code', 'link_message', 'source_file']].copy()
                validation_df.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Validation report exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="Enhanced Business Tools Browser")
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode')
    parser.add_argument('--process', nargs='+', help='Process files and exit (CLI mode)')
    parser.add_argument('--validate', action='store_true', help='Validate links in existing master CSV')
    
    args = parser.parse_args()
    
    if args.cli or args.process or args.validate:
        # CLI mode
        processor = DataProcessor()
        
        if args.process:
            print("Processing files in CLI mode...")
            try:
                def progress_callback(message):
                    print(f"Progress: {message}")
                
                master_df, file_count = processor.process_files(args.process, progress_callback)
                print(f"\nSuccess! Processed {file_count} files with {len(master_df)} total entries.")
                print(f"Master CSV saved to: {processor.master_csv}")
                print(f"Validation report saved to: {processor.validation_report}")
                
            except Exception as e:
                print(f"Error: {str(e)}")
                sys.exit(1)
        
        elif args.validate:
            print("Validating links in existing master CSV...")
            try:
                if processor.master_csv.exists():
                    df = pd.read_csv(processor.master_csv)
                    
                    def progress_callback(message):
                        print(f"Progress: {message}")
                    
                    df = processor.validate_links_with_progress(df, progress_callback)
                    df.to_csv(processor.master_csv, index=False)
                    
                    # Update validation report
                    validation_df = df[['name', 'url', 'link_status', 'link_code', 'link_message', 'source_file']].copy()
                    validation_df.to_csv(processor.validation_report, index=False)
                    
                    print(f"\nValidation completed! Updated {len(df)} entries.")
                    print(f"Results saved to: {processor.master_csv}")
                    
                else:
                    print("No master CSV found. Please process files first.")
                    sys.exit(1)
                    
            except Exception as e:
                print(f"Error: {str(e)}")
                sys.exit(1)
        
        else:
            print("Enhanced Business Tools Browser - CLI Mode")
            print("Use --process [files...] to process files")
            print("Use --validate to validate existing links")
    
    else:
        # GUI mode
        try:
            app = BusinessToolsGUI()
            app.run()
        except Exception as e:
            print(f"Failed to start GUI: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main()
