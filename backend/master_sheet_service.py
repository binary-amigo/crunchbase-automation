import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from datetime import datetime
from config import Config

class MasterSheetService:
    def __init__(self):
        self.config = Config()
        self.creds = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            # Load existing token
            if os.path.exists(self.config.GOOGLE_SHEETS_TOKEN_FILE):
                self.creds = Credentials.from_authorized_user_file(
                    self.config.GOOGLE_SHEETS_TOKEN_FILE, 
                    ['https://www.googleapis.com/auth/spreadsheets']
                )
            
            # If no valid credentials, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.config.GOOGLE_SHEETS_CREDENTIALS_FILE,
                        ['https://www.googleapis.com/auth/spreadsheets']
                    )
                    self.creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(self.config.GOOGLE_SHEETS_TOKEN_FILE, 'w') as token:
                    token.write(self.creds.to_json())
            
            self.service = build('sheets', 'v4', credentials=self.creds)
            
        except Exception as e:
            print(f"ERROR: MasterSheetService authentication failed: {str(e)}")
            raise
    
    def get_existing_companies(self):
        """Get all existing companies from master sheet (for duplicate prevention)"""
        try:
            if not self.config.MASTER_SHEET_ID:
                print("ERROR: MASTER_SHEET_ID not configured")
                return set()
            
            # Get all data from master sheet
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.config.MASTER_SHEET_ID,
                range=f"{self.config.MASTER_SHEET_NAME}!A:C"
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return set()
            
            # Skip header row, extract company names from column B
            existing_companies = set()
            for row in values[1:]:  # Skip header
                if len(row) >= 2 and row[1]:  # Check if Company column has value
                    existing_companies.add(row[1].strip())
            
            return existing_companies
            
        except Exception as e:
            print(f"ERROR: Failed to get existing companies from master sheet: {str(e)}")
            return set()
    
    def add_company_to_master(self, client_name, company_name):
        """Add a single company to the master sheet"""
        try:
            if not self.config.MASTER_SHEET_ID:
                return False, "Master sheet ID not configured"
            
            # Prepare the row data
            row_data = [client_name, company_name, self.config.DEFAULT_VALUES["Date"]]
            
            # Find next available row
            next_row, error = self.find_next_available_row()
            if error:
                return False, f"Failed to find next available row: {error}"
            
            # Add the row
            range_name = f"{self.config.MASTER_SHEET_NAME}!A{next_row}:C{next_row}"
            body = {'values': [row_data]}
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.config.MASTER_SHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            # Apply client-specific background color
            self.apply_client_color(next_row, client_name)
            
            return True, f"Successfully added {company_name} to master sheet"
            
        except Exception as e:
            print(f"ERROR: Failed to add company to master sheet: {str(e)}")
            return False, f"Failed to add company: {str(e)}"
    
    def add_companies_to_master(self, companies_data):
        """Add multiple companies to the master sheet efficiently"""
        try:
            if not self.config.MASTER_SHEET_ID:
                return False, "Master sheet ID not configured"
            
            if not companies_data:
                return True, "No companies to add"
            
            # Find next available row
            next_row, error = self.find_next_available_row()
            if error:
                return False, f"Failed to find next available row: {error}"
            
            # Prepare all rows at once
            rows_data = []
            for company_data in companies_data:
                client_name, company_name, date_added = company_data
                rows_data.append([client_name, company_name, date_added])
            
            # Add all rows in a single API call
            range_name = f"{self.config.MASTER_SHEET_NAME}!A{next_row}:C{next_row + len(rows_data) - 1}"
            body = {'values': rows_data}
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.config.MASTER_SHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            # Apply client-specific background colors for all rows
            for i, company_data in enumerate(companies_data):
                client_name = company_data[0]
                self.apply_client_color(next_row + i, client_name)
            
            return True, f"Successfully added {len(companies_data)} companies to master sheet"
            
        except Exception as e:
            print(f"ERROR: Failed to add companies to master sheet: {str(e)}")
            return False, f"Failed to add companies: {str(e)}"
    
    def find_next_available_row(self):
        """Find the next available row in the master sheet"""
        try:
            if not self.config.MASTER_SHEET_ID:
                return None, "Master sheet ID not configured"
            
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.config.MASTER_SHEET_ID,
                range=f"{self.config.MASTER_SHEET_NAME}!A:C"
            ).execute()
            
            values = result.get('values', [])
            next_row = len(values) + 1
            
            return next_row, None
            
        except Exception as e:
            print(f"ERROR: Failed to find next available row: {str(e)}")
            return None, f"Failed to find next row: {str(e)}"
    
    def apply_client_color(self, row_number, client_name):
        """Apply client-specific background color to a row"""
        try:
            if not self.config.MASTER_SHEET_ID:
                return False, "Master sheet ID not configured"
            
            # Define client colors
            colors = {
                'Client A': {'red': 0.9, 'green': 0.9, 'blue': 1.0},  # Light blue
                'Client B': {'red': 1.0, 'green': 0.9, 'blue': 0.9}   # Light red
            }
            
            if client_name not in colors:
                print(f"WARNING: No color defined for client: {client_name}")
                return False, f"No color defined for client: {client_name}"
            
            color = colors[client_name]
            
            # Apply background color to the entire row
            requests = [{
                'repeatCell': {
                    'range': {
                        'sheetId': self._get_sheet_id(self.config.MASTER_SHEET_NAME),
                        'startRowIndex': row_number - 1,
                        'endRowIndex': row_number,
                        'startColumnIndex': 0,
                        'endColumnIndex': 3
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': color
                        }
                    },
                    'fields': 'userEnteredFormat.backgroundColor'
                }
            }]
            
            body = {'requests': requests}
            result = self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.config.MASTER_SHEET_ID,
                body=body
            ).execute()
            
            return True, f"Applied color to row {row_number}"
            
        except Exception as e:
            print(f"ERROR: Failed to apply client color: {str(e)}")
            return False, f"Failed to apply color: {str(e)}"
    
    def _get_sheet_id(self, sheet_name):
        """Get the sheet ID by name"""
        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.config.MASTER_SHEET_ID
            ).execute()
            
            for sheet in spreadsheet['sheets']:
                if sheet['properties']['title'] == sheet_name:
                    return sheet['properties']['sheetId']
            
            return None
        except Exception as e:
            print(f"ERROR: Failed to get sheet ID: {str(e)}")
            return None
    
    def test_connection(self):
        """Test connection to master sheet"""
        try:
            if not self.config.MASTER_SHEET_ID:
                return False, "MASTER_SHEET_ID not configured"
            
            # Try to get sheet info
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.config.MASTER_SHEET_ID
            ).execute()
            
            sheet_title = spreadsheet['properties']['title']
            return True, f"Connected to master sheet: {sheet_title}"
            
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
    
    def initialize_master_sheet(self):
        """Initialize the master sheet with headers if they don't exist"""
        try:
            if not self.config.MASTER_SHEET_ID:
                return False, "MASTER_SHEET_ID not configured"
            
            # Check if headers already exist
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.config.MASTER_SHEET_ID,
                range=f"{self.config.MASTER_SHEET_NAME}!A1:C1"
            ).execute()
            
            values = result.get('values', [])
            
            # Check if headers already exist
            if len(values) > 0 and values[0] == self.config.MASTER_SHEET_COLUMNS:
                return True, "Master sheet headers already exist"
            
            # Add headers if they don't exist
            range_name = f"{self.config.MASTER_SHEET_NAME}!A1:C1"
            body = {'values': [self.config.MASTER_SHEET_COLUMNS]}
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.config.MASTER_SHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            # Format headers (bold, centered, background color)
            self._format_headers()
            
            return True, "Master sheet initialized with headers"
            
        except Exception as e:
            print(f"ERROR: Failed to initialize master sheet: {str(e)}")
            return False, f"Failed to initialize master sheet: {str(e)}"
    
    def _format_headers(self):
        """Format master sheet headers (bold, centered, background)"""
        try:
            requests = [{
                'repeatCell': {
                    'range': {
                        'sheetId': self._get_sheet_id(self.config.MASTER_SHEET_NAME),
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': 3
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.2},
                            'textFormat': {
                                'bold': True,
                                'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}
                            },
                            'horizontalAlignment': 'CENTER'
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
                }
            }]
            
            body = {'requests': requests}
            result = self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.config.MASTER_SHEET_ID,
                body=body
            ).execute()
            
            return True, "Headers formatted successfully"
            
        except Exception as e:
            print(f"WARNING: Failed to format headers: {str(e)}") 