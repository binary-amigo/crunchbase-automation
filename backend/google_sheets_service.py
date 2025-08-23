import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from datetime import datetime
from config import Config
from master_sheet_service import MasterSheetService

class GoogleSheetsService:
    def __init__(self, client_id=None):
        self.config = Config()
        self.client_id = client_id
        self.creds = None
        self.service = None
        self.master_service = MasterSheetService()
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            # Load existing token
            if os.path.exists(self.config.GOOGLE_SHEETS_CREDENTIALS_FILE):
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
            print(f"ERROR: GoogleSheetsService authentication failed: {str(e)}")
            raise
    
    def get_client_sheet_info(self):
        """Get information about the current client's sheet"""
        if not self.client_id:
            return None, "No client ID specified"
        
        if self.client_id not in self.config.CLIENT_SHEETS:
            return None, f"Unknown client ID: {self.client_id}"
        
        return self.config.CLIENT_SHEETS[self.client_id], None
    
    def get_existing_headers(self):
        """Get existing headers from the client sheet"""
        try:
            client_info, error = self.get_client_sheet_info()
            if error:
                return None, error
            
            sheet_id = client_info['sheet_id']
            sheet_name = client_info['sheet_name']
            
            if not sheet_id:
                return None, f"Sheet ID not configured for {client_info['name']}"
            
            # Get headers from the first row
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f"{sheet_name}!A1:Z1"
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return None, f"No headers found in {sheet_name}"
            
            headers = [header.strip() for header in values[0] if header.strip()]
            return headers, None
            
        except Exception as e:
            print(f"ERROR: Failed to get existing headers: {str(e)}")
            return None, f"Failed to get headers: {str(e)}"
    
    def find_next_available_row(self):
        """Find the next available row in the client sheet"""
        try:
            client_info, error = self.get_client_sheet_info()
            if error:
                return None, error
            
            sheet_id = client_info['sheet_id']
            sheet_name = client_info['sheet_name']
            
            # Get all data to find the last row
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f"{sheet_name}!A:Z"
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return 1, None  # Empty sheet, start at row 1
            
            # Find the last non-empty row
            last_row = 0
            for i, row in enumerate(values):
                if any(cell.strip() for cell in row):
                    last_row = i + 1
            
            next_row = last_row + 1
            return next_row, None
            
        except Exception as e:
            print(f"ERROR: Failed to find next available row: {str(e)}")
            return None, f"Failed to find next row: {str(e)}"
    
    def map_csv_columns_to_sheet(self, csv_columns, sheet_headers):
        """Map CSV column names to sheet column names"""
        try:
            
            mapped_columns = {}
            
            for csv_col in csv_columns:
                csv_col_clean = csv_col.strip()
                
                # First try exact mapping from config
                if csv_col_clean in self.config.COLUMN_MAPPING:
                    sheet_col = self.config.COLUMN_MAPPING[csv_col_clean]
                    if sheet_col in sheet_headers:
                        mapped_columns[sheet_col] = csv_col
                        continue
                
                # Then try direct name matching
                if csv_col_clean in sheet_headers:
                    mapped_columns[csv_col_clean] = csv_col
                    continue
                
                # If no mapping found, log it
                pass
            
            return mapped_columns
            
        except Exception as e:
            print(f"ERROR: Failed to map CSV columns: {str(e)}")
            return {}
    
    def prepare_data_for_sheets(self, data, mapped_columns, sheet_headers):
        """Prepare data for Google Sheets with proper column ordering and default values"""
        try:
            ordered_data = []
            
            for index, row in data.iterrows():
                ordered_row = []
                
                for sheet_col in sheet_headers:
                    if sheet_col in mapped_columns:
                        # This sheet column has a CSV mapping
                        csv_col = mapped_columns[sheet_col]
                        value = str(row[csv_col])
                    else:
                        # This sheet column has no mapping, check for default values
                        value = ""
                    
                    # Apply default values for specific columns (regardless of mapping)
                    if sheet_col in self.config.DEFAULT_VALUES:
                        if sheet_col == "Date":
                            # Always use today's date
                            value = self.config.DEFAULT_VALUES["Date"]
                        elif sheet_col == "Source":
                            # Always use Crunchbase
                            value = self.config.DEFAULT_VALUES["Source"]
                        elif sheet_col in ["POCs", "Email ID", "Reachout LinkedIn", "Reachout Email", "Response"]:
                            # Leave these blank
                            value = ""
                    
                    ordered_row.append(value)
                
                ordered_data.append(ordered_row)
            
            return ordered_data
            
        except Exception as e:
            print(f"ERROR: Failed to prepare data for sheets: {str(e)}")
            return []
    
    def detect_duplicates(self, data, mapped_columns):
        """Efficiently detect duplicates using single master sheet read"""
        try:
            if not self.config.DUPLICATE_CHECK_FIELDS:
                return data
            
            # Single read from master sheet to get all existing companies
            existing_companies = self.master_service.get_existing_companies()
            
            if not existing_companies:
                return data
            
            # Get the company field to check
            company_field = self.config.DUPLICATE_CHECK_FIELDS[0]  # "Company Name"
            if company_field not in mapped_columns:
                return data
            
            csv_col = mapped_columns[company_field]
            
            # Filter DataFrame to only include new companies
            new_companies_mask = ~data[csv_col].str.strip().isin(existing_companies)
            new_companies = data[new_companies_mask].copy()
            
            return new_companies
            
        except Exception as e:
            print(f"ERROR: Failed to detect duplicates: {str(e)}")
            return data
    
    def append_data(self, data, client_name):
        """Efficiently append data to both master sheet and client sheet"""
        try:
            
            # Get client sheet info
            client_info, error = self.get_client_sheet_info()
            if error:
                return False, f"Failed to get client sheet info: {error}"
            
            sheet_id = client_info['sheet_id']
            sheet_name = client_info['sheet_name']
            
            # Get sheet headers
            sheet_headers, error = self.get_existing_headers()
            if error:
                return False, f"Failed to get sheet headers: {error}"
            
            # Map CSV columns to sheet headers
            mapped_columns = self.map_csv_columns_to_sheet(data.columns.tolist(), sheet_headers)
            mapped_count = len([col for col in mapped_columns.values() if col])
            
            if mapped_count == 0:
                return False, "No CSV columns could be mapped to sheet headers"
            
            # Efficient duplicate detection - returns filtered DataFrame
            new_companies_data = self.detect_duplicates(data, mapped_columns)
            
            if len(new_companies_data) == 0:
                return False, f"No new companies to add. All {len(data)} companies already exist in master sheet."
            
            # Prepare data for client sheet (all new companies at once)
            client_sheet_data = self.prepare_data_for_sheets(new_companies_data, mapped_columns, sheet_headers)
            
            if not client_sheet_data:
                return False, "Failed to prepare data for client sheet"
            
            # Find next available row in client sheet
            next_row, error = self.find_next_available_row()
            if error:
                return False, f"Failed to find next available row: {error}"
            
            # Single write to client sheet with all new companies
            range_name = f"{sheet_name}!A{next_row}:{chr(65 + len(sheet_headers) - 1)}{next_row + len(client_sheet_data) - 1}"
            body = {'values': client_sheet_data}
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            # Prepare data for master sheet (just company names, client, and date)
            master_data = []
            company_field = self.config.DUPLICATE_CHECK_FIELDS[0]  # "Company Name"
            csv_col = mapped_columns[company_field]
            
            for _, row in new_companies_data.iterrows():
                company_name = str(row[csv_col]).strip()
                master_data.append([client_name, company_name, self.config.DEFAULT_VALUES["Date"]])
            
            # Single write to master sheet
            master_success, master_message = self.master_service.add_companies_to_master(master_data)
            if not master_success:
                print(f"WARNING: Failed to add companies to master sheet: {master_message}")
                # Continue anyway since client sheet was updated
            
            # Success message
            message_parts = [
                f"Successfully added {len(new_companies_data)} new companies to {client_name} sheet",
                f"Starting from row {next_row}",
                f"Updated master sheet with {len(master_data)} new company entries"
            ]
            
            if len(data) > len(new_companies_data):
                skipped_count = len(data) - len(new_companies_data)
                message_parts.append(f"Skipped {skipped_count} existing companies")
            
            return True, ". ".join(message_parts)
            
        except Exception as e:
            print(f"ERROR: Failed to append data: {str(e)}")
            return False, f"Unexpected error: {str(e)}"
    
    def get_column_mapping_info(self):
        """Get information about column mapping and sheet configuration"""
        try:
            client_info, error = self.get_client_sheet_info()
            if error:
                return None
            
            sheet_headers, error = self.get_existing_headers()
            if error:
                return None
            
            return {
                'client_name': client_info['name'] if client_info else 'Unknown',
                'sheet_name': client_info['sheet_name'] if client_info else 'Unknown',
                'sheet_headers': sheet_headers,
                'csv_mapping': self.config.COLUMN_MAPPING,
                'duplicate_check_fields': self.config.DUPLICATE_CHECK_FIELDS,
                'duplicate_handling': self.config.DUPLICATE_HANDLING,
                'duplicate_min_match_score': self.config.DUPLICATE_MIN_MATCH_SCORE
            }
            
        except Exception as e:
            print(f"ERROR: Failed to get column mapping info: {str(e)}")
            return None
    
    def test_connection(self):
        """Test connection to client sheet"""
        try:
            client_info, error = self.get_client_sheet_info()
            if error:
                return False, error
            
            sheet_id = client_info['sheet_id']
            sheet_name = client_info['sheet_name']
            
            if not sheet_id:
                return False, f"Sheet ID not configured for {client_info['name']}"
            
            # Try to get sheet info
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()
            
            sheet_title = spreadsheet['properties']['title']
            return True, f"Connected to {client_info['name']} sheet: {sheet_title}"
            
        except Exception as e:
            return False, f"Connection test failed: {str(e)}" 