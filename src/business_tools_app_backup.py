#!/usr/bin/env python3
"""
Business Tools Browser - Unified Application (Clean Version)
Combines data processing, GUI, and CLI functionality
No emojis, relative paths, generic Excel file support
"""

import sys
import os
import argparse
import pandas as pd
import requests
from urllib.parse import urlparse
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from pathlib import Path
import glob

# Get application directory
APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data"
RESOURCES_DIR = APP_DIR / "resources"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

def find_excel_file():
    """Find the first Excel file in the current directory or data subdirectory"""
    # Check data subdirectory first
    data_dir = Path('data')
    if data_dir.exists():
        for ext in ['*.xlsx', '*.xls']:
            files = list(data_dir.glob(ext))
            if files:
                return str(files[0])
    
    # Check current directory
    for ext in ['*.xlsx', '*.xls']:
        files = glob.glob(ext)
        if files:
            return files[0]
    
    return None

class DataProcessor:
    """Handles Excel/CSV data processing and cleaning"""
    
    def __init__(self):
        self.source_file = None
        self.cleaned_csv = DATA_DIR / "Cleaned_Tools.csv"
        self.summary_csv = DATA_DIR / "Tools_Summary.csv"
    
    def classify_tool_access(self, row):
        """Classify tool as Internal or Public based on URL and description"""
        url = str(row.get('URL', '')).lower()
        synopsis = str(row.get('Enhanced_Synopsis', '')).lower()
        
        # Internal indicators
        internal_indicators = [
            'redhat.com', 'internal', 'intranet', 'corp', 'employee',
            'staff', 'private', 'restricted', 'confidential'
        ]
        
        # Check URL and description
        for indicator in internal_indicators:
            if indicator in url or indicator in synopsis:
                return 'Internal'
        
        return 'Public'
    
    def enhance_name(self, name):
        """Enhance tool names with descriptions"""
        name_map = {
            "Draw.io": "Draw.io - Web Diagramming Tool",
            "Doitlive": "Doitlive - Terminal Demo Simulator",
            "Skype": "Skype - Web-Based Video & Voice Communication",
            "Trello": "Trello - Visual Project Management Boards",
            "Lucidchart": "Lucidchart - Intelligent Diagramming Platform",
            "Jupyterlab": "JupyterLab - Interactive Data Science Environment"
        }
        return name_map.get(name, name)
    
    def enhance_description(self, row, df):
        """Enhance tool descriptions"""
        synopsis_col = 'Synopsis' if 'Synopsis' in df.columns else 'Description' if 'Description' in df.columns else None
        if synopsis_col is None:
            return "Tool description not available"
        
        synopsis = str(row[synopsis_col]).lower()
        if "diagram" in synopsis:
            return "Tool for creating flowcharts, architecture maps, and process diagrams."
        elif "learning" in synopsis or "labs" in synopsis:
            return "Interactive learning tools and environments for business technologies."
        elif "authentic" in synopsis or "token" in synopsis:
            return "Authentication and identity tools for secure access control."
        elif "stream" in synopsis or "video" in synopsis:
            return "Utilities for recording, streaming, and multimedia editing."
        elif "terminal" in synopsis:
            return "CLI tools for sysadmin workflows and shell automation."
        elif "git" in synopsis:
            return "Repositories or tools for managing source code and collaboration."
        return row[synopsis_col] if synopsis_col in row else "Tool description not available"
    
    def categorize(self, row):
        """Categorize tools based on description"""
        desc = str(row["Enhanced_Synopsis"]).lower()
        if "authentication" in desc or "token" in desc:
            return "Security"
        elif "learning" in desc or "labs" in desc or "training" in desc:
            return "Education"
        elif "diagram" in desc:
            return "Diagramming"
        elif "stream" in desc or "video" in desc or "recording" in desc:
            return "Media Tools"
        elif "git" in desc or "repository" in desc:
            return "Code Repositories"
        elif "meeting" in desc or "conference" in desc:
            return "Meetings"
        elif "automation" in desc or "ansible" in desc:
            return "Automation"
        elif "terminal" in desc:
            return "CLI Utilities"
        return "General Utilities"
    
    def check_url(self, url):
        """Check URL accessibility"""
        try:
            response = requests.head(url, allow_redirects=True, timeout=6)
            if response.status_code == 200:
                return "OK"
            elif response.status_code == 403:
                return "Restricted"
            else:
                return f"Error {response.status_code}"
        except:
            return "Invalid"
    
    def process_excel_file(self, file_path, progress_callback=None):
        """Process Excel file and create cleaned CSV"""
        try:
            if progress_callback:
                progress_callback("Loading Excel file...")
            
            # Read Excel file
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                xls_dict = pd.read_excel(file_path, sheet_name=None)
                if len(xls_dict) == 1:
                    df = list(xls_dict.values())[0]
                else:
                    sheet_names = list(xls_dict.keys())
                    df = xls_dict[sheet_names[0]]
            
            if progress_callback:
                progress_callback("Cleaning column names...")
            
            # Fix column names
            df.columns = [col.strip().title().replace(" ", "_") for col in df.columns]
            
            # Map common column variations
            column_mapping = {
                'Url': 'URL',
                'Link': 'URL',
                'Links': 'URL', 
                'Web_Link': 'URL',
                'Tool_Name': 'Name',
                'Title': 'Name',
                'Description': 'Synopsis',
                'Type': 'Tool_Type',
                'Category': 'Tool_Type'
            }
            
            for old_name, new_name in column_mapping.items():
                if old_name in df.columns and new_name not in df.columns:
                    df.rename(columns={old_name: new_name}, inplace=True)
            
            if progress_callback:
                progress_callback("Validating URLs...")
            
            # Validate URLs if column exists
            if 'URL' in df.columns:
                df["URL"] = df["URL"].astype(str).str.strip()
                df["URL_Status"] = df["URL"].apply(self.check_url)
                df = df[df["URL_Status"] == "OK"]
            
            if progress_callback:
                progress_callback("Enhancing descriptions...")
            
            # Enhance names and descriptions
            if 'Name' in df.columns:
                df["Name"] = df["Name"].apply(self.enhance_name)
            
            df["Enhanced_Synopsis"] = df.apply(lambda row: self.enhance_description(row, df), axis=1)
            df["Category"] = df.apply(self.categorize, axis=1)
            df["Access_Level"] = df.apply(self.classify_tool_access, axis=1)
            
            if progress_callback:
                progress_callback("Saving results...")
            
            # Save results
            df.to_csv(self.cleaned_csv, index=False)
            summary = df["Category"].value_counts().reset_index()
            summary.columns = ["Category", "Tool_Count"]
            summary.to_csv(self.summary_csv, index=False)
            
            if progress_callback:
                progress_callback("Complete!")
            
            return True, f"Processed {len(df)} tools successfully"
            
        except Exception as e:
            return False, f"Error processing file: {str(e)}"


class BusinessToolsGUI:
    """GUI interface for Business Tools Browser"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Business Tools Browser")
        self.root.geometry("1000x700")
        
        # Try to set icon
        try:
            icon_path = RESOURCES_DIR / "business_tools.png"
            if icon_path.exists():
                self.root.iconphoto(False, tk.PhotoImage(file=str(icon_path)))
        except:
            pass
        
        self.processor = DataProcessor()
        self.df = None
        self.filtered_df = None
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Business Tools Browser", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Search & Filter", padding="5")
        control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)
        
        # Search
        ttk.Label(control_frame, text="Search:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=40)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        # Category filter
        ttk.Label(control_frame, text="Category:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(control_frame, textvariable=self.category_var, 
                                          state="readonly", width=15)
        self.category_combo.grid(row=0, column=3, padx=(0, 10))
        self.category_combo.bind('<<ComboboxSelected>>', self.on_filter)
        
        # Access level filter
        ttk.Label(control_frame, text="Access:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.access_var = tk.StringVar()
        self.access_combo = ttk.Combobox(control_frame, textvariable=self.access_var,
                                        values=["All", "Public", "Internal"],
                                        state="readonly", width=10)
        self.access_combo.set("All")
        self.access_combo.grid(row=0, column=5, padx=(0, 10))
        self.access_combo.bind('<<ComboboxSelected>>', self.on_filter)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=6, padx=(10, 0))
        
        ttk.Button(button_frame, text="Load File", 
                  command=self.load_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_search).pack(side=tk.LEFT)
        
        # Results tree
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Treeview with scrollbars
        self.tree = ttk.Treeview(tree_frame, columns=("Category", "Access", "Description"), 
                                show="tree headings", height=20)
        
        # Column configuration
        self.tree.heading("#0", text="Tool Name")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Access", text="Access Level")
        self.tree.heading("Description", text="Description")
        
        self.tree.column("#0", width=200, minwidth=150)
        self.tree.column("Category", width=120, minwidth=100)
        self.tree.column("Access", width=80, minwidth=80)
        self.tree.column("Description", width=400, minwidth=300)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for tree and scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind double-click
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def load_data(self):
        """Load data from CSV file"""
        try:
            if self.processor.cleaned_csv.exists():
                self.df = pd.read_csv(self.processor.cleaned_csv)
                self.populate_tree()
                self.update_filters()
                self.status_var.set(f"Loaded {len(self.df)} tools")
            else:
                # Try to find and process an Excel file automatically
                excel_file = find_excel_file()
                if excel_file:
                    success, message = self.processor.process_excel_file(excel_file)
                    if success:
                        self.df = pd.read_csv(self.processor.cleaned_csv)
                        self.populate_tree()
                        self.update_filters()
                        self.status_var.set(f"Loaded {len(self.df)} tools from {excel_file}")
                    else:
                        self.status_var.set(f"Error processing {excel_file}: {message}")
                else:
                    self.status_var.set("No data file found. Please load an Excel file.")
        except Exception as e:
            self.status_var.set(f"Error loading data: {str(e)}")
    
    def load_file(self):
        """Load and process an Excel file"""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            # Progress dialog
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Processing File")
            progress_window.geometry("400x100")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            progress_label = ttk.Label(progress_window, text="Starting...")
            progress_label.pack(pady=20)
            
            def update_progress(message):
                progress_label.config(text=message)
                progress_window.update()
            
            # Process file
            success, message = self.processor.process_excel_file(file_path, update_progress)
            
            progress_window.destroy()
            
            if success:
                self.load_data()
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
    
    def populate_tree(self):
        """Populate the tree with data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.df is None:
            return
        
        # Use filtered data if available
        data = self.filtered_df if self.filtered_df is not None else self.df
        
        for _, row in data.iterrows():
            name = row.get('Name', 'Unknown')
            category = row.get('Category', 'Unknown')
            access = row.get('Access_Level', 'Unknown')
            description = row.get('Enhanced_Synopsis', 'No description')
            
            # Truncate long descriptions
            if len(description) > 100:
                description = description[:97] + "..."
            
            self.tree.insert("", tk.END, text=name, 
                           values=(category, access, description),
                           tags=(row.name,))  # Store row index in tags
    
    def update_filters(self):
        """Update filter dropdown options"""
        if self.df is None:
            return
        
        # Update category options
        categories = ["All"] + sorted(self.df['Category'].unique().tolist())
        self.category_combo['values'] = categories
        self.category_combo.set("All")
    
    def on_search(self, event=None):
        """Handle search input"""
        self.apply_filters()
    
    def on_filter(self, event=None):
        """Handle filter changes"""
        self.apply_filters()
    
    def apply_filters(self):
        """Apply search and filter criteria"""
        if self.df is None:
            return
        
        # Start with full dataset
        filtered = self.df.copy()
        
        # Apply search filter
        search_text = self.search_var.get().lower()
        if search_text:
            mask = (filtered['Name'].str.lower().str.contains(search_text, na=False) |
                   filtered['Enhanced_Synopsis'].str.lower().str.contains(search_text, na=False))
            filtered = filtered[mask]
        
        # Apply category filter
        category = self.category_var.get()
        if category and category != "All":
            filtered = filtered[filtered['Category'] == category]
        
        # Apply access level filter
        access = self.access_var.get()
        if access and access != "All":
            filtered = filtered[filtered['Access_Level'] == access]
        
        self.filtered_df = filtered
        self.populate_tree()
        self.status_var.set(f"Showing {len(filtered)} of {len(self.df)} tools")
    
    def clear_search(self):
        """Clear all search and filter criteria"""
        self.search_var.set("")
        self.category_var.set("All")
        self.access_var.set("All")
        self.filtered_df = None
        self.populate_tree()
        self.status_var.set(f"Showing all {len(self.df)} tools")
    
    def on_double_click(self, event):
        """Handle double-click on tree item"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        if not item['tags']:
            return
        
        try:
            row_index = int(item['tags'][0])
            data = self.filtered_df if self.filtered_df is not None else self.df
            url = data.iloc[row_index].get('URL', '')
            
            if url and url != 'nan':
                webbrowser.open(url)
            else:
                messagebox.showwarning("No URL", "No URL available for this tool.")
        except (ValueError, IndexError, KeyError):
            messagebox.showerror("Error", "Could not open tool URL.")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


class BusinessToolsCLI:
    """CLI interface for Business Tools Browser"""
    
    def __init__(self):
        self.processor = DataProcessor()
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Load data from CSV file"""
        try:
            if self.processor.cleaned_csv.exists():
                self.df = pd.read_csv(self.processor.cleaned_csv)
            else:
                # Try to find and process an Excel file automatically
                excel_file = find_excel_file()
                if excel_file:
                    print(f"Found Excel file: {excel_file}")
                    print("Processing...")
                    success, message = self.processor.process_excel_file(excel_file)
                    if success:
                        self.df = pd.read_csv(self.processor.cleaned_csv)
                        print(f"SUCCESS: {message}")
                    else:
                        print(f"ERROR: {message}")
                else:
                    print("No data file found. Please process an Excel file first.")
        except Exception as e:
            print(f"Error loading data: {str(e)}")
    
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*50)
        print("        BUSINESS TOOLS BROWSER")
        print("="*50)
        print("1. Browse All Tools")
        print("2. Search Tools")
        print("3. Browse by Category") 
        print("4. Browse by Access Level")
        print("5. Load New Excel File")
        print("6. Show Statistics")
        print("7. Exit")
        print("="*50)
    
    def browse_all_tools(self):
        """Display all tools"""
        if self.df is None:
            print("No data available.")
            return
        
        print(f"\nAll Tools ({len(self.df)} total):")
        print("-" * 80)
        
        for _, row in self.df.iterrows():
            name = row.get('Name', 'Unknown')
            category = row.get('Category', 'Unknown')
            access = row.get('Access_Level', 'Unknown')
            description = row.get('Enhanced_Synopsis', 'No description')
            
            print(f"Name: {name}")
            print(f"Category: {category} | Access: {access}")
            print(f"Description: {description[:100]}{'...' if len(description) > 100 else ''}")
            print("-" * 80)
    
    def search_tools(self):
        """Search for tools"""
        if self.df is None:
            print("No data available.")
            return
        
        query = input("Enter search term: ").lower()
        if not query:
            return
        
        # Search in name and description
        mask = (self.df['Name'].str.lower().str.contains(query, na=False) |
               self.df['Enhanced_Synopsis'].str.lower().str.contains(query, na=False))
        results = self.df[mask]
        
        print(f"\nSearch results for '{query}' ({len(results)} found):")
        print("-" * 80)
        
        for _, row in results.iterrows():
            name = row.get('Name', 'Unknown')
            category = row.get('Category', 'Unknown')
            access = row.get('Access_Level', 'Unknown')
            url = row.get('URL', 'No URL')
            
            print(f"Name: {name}")
            print(f"Category: {category} | Access: {access}")
            print(f"URL: {url}")
            print("-" * 80)
    
    def browse_by_category(self):
        """Browse tools by category"""
        if self.df is None:
            print("No data available.")
            return
        
        categories = sorted(self.df['Category'].unique())
        
        print("\nAvailable Categories:")
        for i, category in enumerate(categories, 1):
            count = len(self.df[self.df['Category'] == category])
            print(f"{i}. {category} ({count} tools)")
        
        try:
            choice = int(input(f"\nSelect category (1-{len(categories)}): ")) - 1
            if 0 <= choice < len(categories):
                selected_category = categories[choice]
                tools = self.df[self.df['Category'] == selected_category]
                
                print(f"\nTools in {selected_category} category:")
                print("-" * 80)
                
                for _, row in tools.iterrows():
                    name = row.get('Name', 'Unknown')
                    access = row.get('Access_Level', 'Unknown')
                    description = row.get('Enhanced_Synopsis', 'No description')
                    
                    print(f"Name: {name} | Access: {access}")
                    print(f"Description: {description[:100]}{'...' if len(description) > 100 else ''}")
                    print("-" * 40)
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
    
    def browse_by_access_level(self):
        """Browse tools by access level"""
        if self.df is None:
            print("No data available.")
            return
        
        access_levels = sorted(self.df['Access_Level'].unique())
        
        print("\nAvailable Access Levels:")
        for i, level in enumerate(access_levels, 1):
            count = len(self.df[self.df['Access_Level'] == level])
            print(f"{i}. {level} ({count} tools)")
        
        try:
            choice = int(input(f"\nSelect access level (1-{len(access_levels)}): ")) - 1
            if 0 <= choice < len(access_levels):
                selected_level = access_levels[choice]
                tools = self.df[self.df['Access_Level'] == selected_level]
                
                print(f"\n{selected_level} Tools:")
                print("-" * 80)
                
                for _, row in tools.iterrows():
                    name = row.get('Name', 'Unknown')
                    category = row.get('Category', 'Unknown')
                    description = row.get('Enhanced_Synopsis', 'No description')
                    
                    print(f"Name: {name} | Category: {category}")
                    print(f"Description: {description[:100]}{'...' if len(description) > 100 else ''}")
                    print("-" * 40)
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
    
    def load_excel_file(self):
        """Load and process Excel file"""
        file_path = input("Enter Excel file path: ").strip()
        if not file_path or not os.path.exists(file_path):
            print("File not found.")
            return
        
        print("Processing file...")
        success, message = self.processor.process_excel_file(file_path)
        
        if success:
            print(f"Success: {message}")
            self.load_data()
        else:
            print(f"Error: {message}")
    
    def show_statistics(self):
        """Show data statistics"""
        if self.df is None:
            print("No data available.")
            return
        
        print(f"\nBusiness Tools Statistics:")
        print("-" * 40)
        print(f"Total Tools: {len(self.df)}")
        
        print(f"\nBy Category:")
        category_counts = self.df['Category'].value_counts()
        for category, count in category_counts.items():
            print(f"  {category}: {count}")
        
        print(f"\nBy Access Level:")
        access_counts = self.df['Access_Level'].value_counts()
        for access, count in access_counts.items():
            print(f"  {access}: {count}")
    
    def run(self):
        """Run the CLI application"""
        while True:
            self.display_menu()
            try:
                choice = int(input("\nSelect option (1-7): "))
                
                if choice == 1:
                    self.browse_all_tools()
                elif choice == 2:
                    self.search_tools()
                elif choice == 3:
                    self.browse_by_category()
                elif choice == 4:
                    self.browse_by_access_level()
                elif choice == 5:
                    self.load_excel_file()
                elif choice == 6:
                    self.show_statistics()
                elif choice == 7:
                    print("Goodbye!")
                    break
                else:
                    print("Invalid option. Please try again.")
                
                input("\nPress Enter to continue...")
                
            except ValueError:
                print("Invalid input. Please enter a number.")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="Business Tools Browser")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--process", type=str, help="Process Excel file and exit")
    
    args = parser.parse_args()
    
    if args.process:
        # Process file mode
        processor = DataProcessor()
        success, message = processor.process_excel_file(args.process)
        print(message)
        sys.exit(0 if success else 1)
    
    elif args.cli:
        # CLI mode
        app = BusinessToolsCLI()
        app.run()
    
    else:
        # GUI mode (default)
        app = BusinessToolsGUI()
        app.run()


if __name__ == "__main__":
    main()
