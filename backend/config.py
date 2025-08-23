import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class Config:
    # Google Sheets Configuration
    GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE', 'credentials.json')
    GOOGLE_SHEETS_TOKEN_FILE = os.getenv('GOOGLE_SHEETS_TOKEN_FILE', 'token.json')
    
    # Master Sheet (Global Registry for Duplicate Prevention)
    MASTER_SHEET_ID = os.getenv('MASTER_SHEET_ID', '')
    MASTER_SHEET_NAME = os.getenv('MASTER_SHEET_NAME', 'Master Registry')
    
    # Client Sheets (Separate sheets for each client's data)
    CLIENT_SHEETS = {
        'client_a': {
            'name': os.getenv('CLIENT_A_NAME', 'Client A'),
            'sheet_id': os.getenv('CLIENT_A_SHEET_ID', ''),
            'sheet_name': os.getenv('CLIENT_A_SHEET_NAME', 'Client A Data')
        },
        'client_b': {
            'name': os.getenv('CLIENT_B_NAME', 'Client B'),
            'sheet_id': os.getenv('CLIENT_B_SHEET_ID', ''),
            'sheet_name': os.getenv('CLIENT_B_SHEET_NAME', 'Client B Data')
        }
    }
    
    # Master Sheet Column Structure (3 columns only)
    MASTER_SHEET_COLUMNS = [
        "Client Name",
        "Company", 
        "Date Added"
    ]
    
    # Column mapping: CSV column name -> Client Sheet column name
    COLUMN_MAPPING = {
        "Organization Name": "Company Name",      # Map this CSV column
        "Website": "Website",                     # Direct Map
        "LinkedIn": "Company Linkedin",           # Direct Map
        "Last Funding Type": "Campaign"           # Map this CSV column
    }
    
    # Default values for specific columns
    DEFAULT_VALUES = {
        "Date": datetime.now().strftime("%d/%m/%y"),  # Today's date in DD/MM/YY format
        "Source": "Crunchbase",  # Always set to Crunchbase
        "Company Name": "",  # Will be filled from CSV Organization Name
        "Website": "",  # Will be filled from CSV Website
        "Company Linkedin": "",  # Will be filled from CSV LinkedIn
        "Campaign": "",  # Will be filled from CSV Last Funding Type
        "POCs": "",  # Leave Blank (No Data)
        "Linkedin ID": "",  # Leave Blank (No Data)
        "Email ID": "",  # Leave Blank (No Data)
        "Reachout LinkedIn": "",  # Leave Blank (No Data)
        "Reachout Email": "",  # Leave Blank (No Data)
        "Response": ""  # Leave Blank (No Data)
    }
    
    # Duplicate detection settings - COMPANY NAME ONLY (global prevention)
    DUPLICATE_CHECK_FIELDS = [
        "Company Name",  # Only check this field for duplicates
    ]
    
    DUPLICATE_HANDLING = os.getenv('DUPLICATE_HANDLING', 'skip').lower()
    
    # Minimum match score required to consider a row as duplicate (0.0 to 1.0)
    # With only Company Name checking, this should be 1.0 (100% match required)
    DUPLICATE_MIN_MATCH_SCORE = float(os.getenv('DUPLICATE_MIN_MATCH_SCORE', '1.0'))
    
    AUTO_MAP_COLUMNS = os.getenv('AUTO_MAP_COLUMNS', 'true').lower() == 'true'
    APPEND_TO_NEXT_ROW = os.getenv('APPEND_TO_NEXT_ROW', 'true').lower() == 'true'
    
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'csv'}
    
    # Processing settings
    BATCH_SIZE = 1000  # Number of rows to process in each batch 