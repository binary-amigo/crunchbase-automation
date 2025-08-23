import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class Config:
    def __init__(self):
        # Google Sheets Configuration
        self.MASTER_SHEET_ID = os.getenv('MASTER_SHEET_ID')
        self.MASTER_SHEET_NAME = os.getenv('MASTER_SHEET_NAME', 'Master')
        self.MASTER_SHEET_COLUMNS = ['Client Name', 'Company', 'Date Added']
        
        # Client Sheets Configuration
        self.CLIENT_SHEETS = {
            'client_a': {
                'name': os.getenv('CLIENT_A_NAME', 'Client A'),
                'sheet_id': os.getenv('CLIENT_A_SHEET_ID'),
                'sheet_name': os.getenv('CLIENT_A_SHEET_NAME', 'Sheet1')
            },
            'client_b': {
                'name': os.getenv('CLIENT_B_NAME', 'Client B'),
                'sheet_id': os.getenv('CLIENT_B_SHEET_ID'),
                'sheet_name': os.getenv('CLIENT_B_SHEET_NAME', 'Sheet1')
            }
        }
        
        # Google API Configuration
        self.GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE', 'credentials.json')
        self.GOOGLE_SHEETS_TOKEN_FILE = os.getenv('GOOGLE_SHEETS_TOKEN_FILE', 'token.json')
        
        # Try to get credentials from environment variables first
        self.GOOGLE_SHEETS_CREDENTIALS = self._get_credentials_from_env()
        
        # File Upload Configuration
        self.UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
        self.ALLOWED_EXTENSIONS = {'csv'}
        self.MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB default
        
        # Column Mapping Configuration
        self.COLUMN_MAPPING = {
            'Organization Name': 'Company Name',
            'Website': 'Website',
            'LinkedIn': 'Company Linkedin',
            'Last Funding Type': 'Campaign'
        }
        
        # Default Values Configuration
        self.DEFAULT_VALUES = {
            'Date': os.getenv('DEFAULT_DATE', '23/08/25'),  # Today's date
            'Source': os.getenv('DEFAULT_SOURCE', 'Crunchbase')
        }
        
        # Duplicate Detection Configuration
        self.DUPLICATE_CHECK_FIELDS = ['Company Name']
        self.DUPLICATE_MIN_MATCH_SCORE = 1.0  # Exact match only
    
    def _get_credentials_from_env(self):
        """Get Google credentials from environment variables if available"""
        credentials_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
        if credentials_json:
            try:
                return json.loads(credentials_json)
            except json.JSONDecodeError:
                print("WARNING: Invalid GOOGLE_SHEETS_CREDENTIALS JSON in environment")
                return None
        return None 