# Enhanced Business Tools Browser

A comprehensive tool for processing, validating, and browsing business tools data from multiple file formats.

## Features

### 🗂️ Multi-Format Support
- **Excel Files**: `.xlsx`, `.xls` (supports multiple sheets)
- **CSV Files**: `.csv` (multiple encoding support)
- **Batch Processing**: Process multiple files simultaneously
- **Data Standardization**: Automatic column mapping and standardization

### 🔗 Link Validation
- **Concurrent Validation**: Fast multi-threaded link checking
- **Comprehensive Status**: Valid, Invalid, Timeout, Connection Error
- **Progress Tracking**: Real-time validation progress
- **Detailed Reports**: HTTP status codes and error messages

### 📊 Data Management
- **Master CSV**: Combined data from all sources in `data/Master_Tools.csv`
- **Duplicate Removal**: Automatic deduplication based on URLs
- **Source Tracking**: Track which file each entry came from
- **Access Classification**: Automatic Internal/Public classification

### 🖥️ User Interfaces
- **GUI Mode**: Full-featured graphical interface with tabs
- **CLI Mode**: Command-line processing for automation
- **Data Browser**: Search, filter, and browse all tools
- **Validation Dashboard**: Link status overview and statistics

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/BusinessToolsBrowser.git
   cd BusinessToolsBrowser
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup the application**:
   ```bash
   ./setup.sh
   ```

4. **Optional system-wide installation**:
   ```bash
   sudo ./install.sh
   ```

## Usage

### GUI Mode (Recommended)
```bash
python3 business_tools.py
```

The GUI provides three main tabs:

#### 📁 File Processing Tab
- Select multiple XLS/XLSX/CSV files
- Process them with real-time progress
- Automatic data standardization and validation

#### 🔍 Data Browser Tab  
- Browse all processed tools
- Search and filter functionality
- Double-click URLs to open in browser

#### ✅ Link Validation Tab
- Validation statistics and status overview
- Re-validate links as needed
- Export validation reports

### CLI Mode
```bash
# Process multiple files
python3 business_tools.py --cli --process file1.xlsx file2.csv file3.xls

# Validate existing links
python3 business_tools.py --cli --validate

# Show help
python3 business_tools.py --help
```

## File Format Requirements

The tool automatically maps common column variations to standard fields:

### Supported Column Names (case-insensitive):

| Standard Field | Accepted Variations |
|----------------|-------------------|
| **name** | name, tool_name, tool, title, application, service |
| **description** | description, desc, summary, overview, about |
| **url** | url, link, website, web_address, site |
| **category** | category, type, classification, group |
| **access** | access, availability, access_type, public, internal |
| **notes** | notes, comments, remarks, additional_info |

### Example Excel/CSV Structure:
```
Tool Name          | Description           | Website URL        | Category
Business Tool 1    | Project management   | https://tool1.com  | Management
Internal Tool      | Company intranet     | http://internal... | Internal
```

## Output Files

### `data/Master_Tools.csv`
Combined and standardized data from all processed files with:
- Standardized column names
- Link validation status
- Source file tracking
- Access classification
- Processing timestamps

### `data/Link_Validation_Report.csv`  
Detailed link validation results with:
- URL status (valid, invalid, timeout, etc.)
- HTTP response codes
- Error messages
- Last validation timestamp

## Link Validation Status

| Status | Description |
|--------|-------------|
| **valid** | Link is accessible (HTTP 2xx/3xx) |
| **error** | HTTP error (4xx/5xx response) |
| **timeout** | Request timed out |
| **connection_error** | Unable to connect |
| **invalid** | Malformed URL |
| **empty** | No URL provided |

## Access Classification

The tool automatically classifies tools as:

- **Internal**: Contains keywords like 'internal', 'intranet', 'corp', private IPs
- **Public**: External services, public domains
- **Unknown**: Cannot determine access type

## Advanced Features

### Batch Processing
Process multiple files at once with progress tracking:
```bash
python3 business_tools.py --process *.xlsx *.csv
```

### Link Re-validation
Update link status for existing data:
```bash
python3 business_tools.py --validate
```

### Data Filtering
GUI provides real-time filtering by:
- Tool name
- Description
- Category
- URL

### Export Options
- Master CSV for all tools
- Validation reports
- Filtered data sets

## Configuration

### Link Validation Settings
Edit `src/business_tools_app.py` to adjust:
- `timeout`: Request timeout (default: 10 seconds)
- `max_workers`: Concurrent validation threads (default: 20)

### Column Mapping
Customize column mappings in the `column_mappings` dictionary for your specific data format.

## Troubleshooting

### Common Issues

1. **Import Errors**: Install missing dependencies with `pip install -r requirements.txt`

2. **File Encoding Issues**: The tool tries multiple encodings automatically

3. **Excel Sheet Selection**: Multiple sheets are automatically combined

4. **Memory Usage**: For large files, consider processing in smaller batches

### Error Messages

- **"File not found"**: Check file path and permissions
- **"Unsupported format"**: Only XLS/XLSX/CSV files supported  
- **"Failed to read file"**: Check file corruption or format

## API Reference

### DataProcessor Class
- `process_files(file_paths, progress_callback)`: Process multiple files
- `validate_links_with_progress(df, progress_callback)`: Validate URLs
- `standardize_columns(df)`: Standardize column names

### LinkValidator Class  
- `validate_url(url)`: Validate single URL
- `validate_urls_batch(urls, progress_callback)`: Batch validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the example files in the `data/` directory
