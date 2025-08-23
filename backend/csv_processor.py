import pandas as pd
import os
from typing import Tuple, Optional

class CSVProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = None
        self.error = None
    
    def process_csv(self) -> Tuple[bool, Optional[pd.DataFrame], str]:
        """
        Process the CSV file and return the data
        
        Returns:
            Tuple[bool, Optional[pd.DataFrame], str]: (success, data, message)
        """
        try:
            # Check if file exists
            if not os.path.exists(self.file_path):
                return False, None, f"File not found: {self.file_path}"
            
            # Read CSV file
            self.data = pd.read_csv(self.file_path)
            
            # Basic validation
            if self.data.empty:
                return False, None, "CSV file is empty"
            
            # Get basic info
            rows, cols = self.data.shape
            
            # Clean the data
            self._clean_data()
            
            return True, self.data, f"CSV processed successfully: {rows} rows, {cols} columns"
            
        except pd.errors.EmptyDataError:
            return False, None, "CSV file is empty or corrupted"
        except pd.errors.ParserError as e:
            return False, None, f"Error parsing CSV: {str(e)}"
        except Exception as e:
            return False, None, f"Unexpected error processing CSV: {str(e)}"
    
    def _clean_data(self):
        """Clean and prepare the data for Google Sheets"""
        if self.data is None:
            return
        
        # Remove completely empty rows
        self.data = self.data.dropna(how='all')
        
        # Remove completely empty columns
        self.data = self.data.dropna(axis=1, how='all')
        
        # Fill NaN values with empty string for better Google Sheets compatibility
        self.data = self.data.fillna('')
        
        # Convert all data to string to avoid Google Sheets formatting issues
        for col in self.data.columns:
            self.data[col] = self.data[col].astype(str)
        
        # Clean column names (remove special characters that might cause issues)
        self.data.columns = [str(col).strip().replace('\n', ' ').replace('\r', ' ') 
                           for col in self.data.columns]
    
    def get_sample_data(self, n_rows: int = 5) -> pd.DataFrame:
        """Get a sample of the data for preview"""
        if self.data is None:
            return pd.DataFrame()
        return self.data.head(n_rows)
    
    def get_data_info(self) -> dict:
        """Get information about the processed data"""
        if self.data is None:
            return {}
        
        return {
            'rows': len(self.data),
            'columns': len(self.data.columns),
            'column_names': list(self.data.columns),
            'file_size_mb': round(os.path.getsize(self.file_path) / (1024 * 1024), 2)
        }
    
    def validate_data(self) -> Tuple[bool, list]:
        """Validate the data and return any issues found"""
        issues = []
        
        if self.data is None:
            return False, ["No data loaded"]
        
        # Check for very long text that might exceed Google Sheets limits
        for col in self.data.columns:
            max_length = self.data[col].str.len().max()
            if max_length > 50000:  # Google Sheets cell limit is ~50k characters
                issues.append(f"Column '{col}' contains text longer than 50,000 characters")
        
        # Check for very wide data
        if len(self.data.columns) > 26:  # More than A-Z columns
            issues.append("CSV has more than 26 columns, which might cause display issues")
        
        # Check for very long data
        if len(self.data) > 100000:  # More than 100k rows
            issues.append("CSV has more than 100,000 rows, which might be slow to process")
        
        return len(issues) == 0, issues 