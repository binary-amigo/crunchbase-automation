# CSV Upload & Master Sheet Backend

A Python Flask backend that processes CSV files and uploads data to Google Sheets with global duplicate prevention and client data isolation.

## 🏗️ **System Architecture**

### **Master Sheet (Global Registry)**
- **Purpose**: Prevents duplicate companies across all clients
- **Columns**: Client Name, Company, Date Added
- **Background Colors**: Different colors for each client for visual separation

### **Client Sheets (Data Storage)**
- **Purpose**: Store full CSV data for each client separately
- **Structure**: Your existing sheet columns (Date, Source, Campaign, Company Name, etc.)
- **Isolation**: Each client only sees their own data

## 🚀 **Features**

- **Global Duplicate Prevention**: Master sheet prevents any company from being added twice anywhere
- **Client Data Isolation**: Each client has their own sheet with no cross-contamination
- **Visual Client Separation**: Master sheet shows different background colors for each client
- **Real-time Progress Tracking**: Monitor upload progress with detailed status updates
- **Smart Column Mapping**: Automatically maps CSV columns to sheet columns
- **Background Processing**: CSV processing and upload happens asynchronously
- **Comprehensive Error Handling**: Detailed error messages and logging

## 📋 **Prerequisites**

- Python 3.8+
- Google Cloud Project with Google Sheets API enabled
- OAuth 2.0 credentials for Google Sheets API
- Three Google Sheets (Master + Client A + Client B)

## 🔧 **Quick Start**

### **1. Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

### **2. Configure Environment**
1. Copy `env.example` to `.env`
2. Fill in your Google Sheets IDs and client configuration
3. Place `credentials.json` in the backend folder

### **3. Run the Backend**
```bash
python app.py
```

Or use the convenience script:
```bash
chmod +x run.sh
./run.sh
```

## 📊 **How It Works**

### **Upload Flow:**
1. **Select Client**: Choose Client A or Client B
2. **Upload CSV**: File is uploaded to backend
3. **Check Master Sheet**: Backend checks if companies already exist globally
4. **Skip Duplicates**: Companies that exist anywhere are skipped
5. **Add New Companies**: New companies are added to:
   - Master sheet (with client info and background color)
   - Client sheet (with full CSV data)
6. **Visual Separation**: Master sheet shows different background colors for each client

### **Duplicate Prevention:**
- **Global Check**: Master sheet prevents any company from being added twice anywhere
- **Client Isolation**: Each client sheet only contains their own data
- **Visual Tracking**: Master sheet shows which client added each company

## 🔌 **API Endpoints**

- `POST /api/upload` - Upload CSV with client selection
- `GET /api/status/<filename>` - Check processing status
- `GET /api/clients` - Get available clients
- `GET /api/column-mapping/<client_id>` - Get column mapping info
- `GET /api/test-master-connection` - Test master sheet connection
- `GET /api/test-client-connection/<client_id>` - Test client sheet connection
- `GET /api/health` - Health check

## 📁 **File Structure**

```
backend/
├── app.py                    # Main Flask application
├── config.py                 # Configuration management
├── master_sheet_service.py   # Master sheet operations
├── google_sheets_service.py  # Client sheet operations
├── csv_processor.py          # CSV processing logic
├── requirements.txt          # Python dependencies
├── .env                      # Environment configuration
├── credentials.json          # Google OAuth credentials
├── setup_guide.md            # Detailed setup instructions
└── README.md                 # This file
```

## ⚙️ **Configuration**

### **Environment Variables**
- `MASTER_SHEET_ID`: Google Sheet ID for master company registry
- `CLIENT_A_SHEET_ID`: Google Sheet ID for Client A data
- `CLIENT_B_SHEET_ID`: Google Sheet ID for Client B data
- `DUPLICATE_HANDLING`: How to handle duplicates (skip/update/append)
- `DUPLICATE_MIN_MATCH_SCORE`: Minimum score for duplicate detection

### **Column Mapping**
Configure CSV to sheet column mapping in `config.py`:
```python
COLUMN_MAPPING = {
    "Organization Name": "Company Name",
    "Website": "Website",
    "LinkedIn": "Company Linkedin",
    "Last Funding Type": "Campaign"
}
```

## 🎯 **Example Usage**

### **Upload CSV for Client A:**
1. Select "Client A" in frontend
2. Upload CSV file
3. System checks master sheet for duplicates
4. New companies added to master sheet (Light Blue background)
5. Full data added to Client A sheet

### **Upload CSV for Client B:**
1. Select "Client B" in frontend
2. Upload CSV file
3. System checks master sheet for duplicates
4. Companies already in master sheet are skipped
5. New companies added to master sheet (Light Green background)
6. Full data added to Client B sheet

## 🛠️ **Troubleshooting**

### **Common Issues:**
- **"Client secrets must be for a web or installed app"**: Recreate credentials as "Desktop application"
- **"Access blocked: App not verified"**: Click "Advanced" → "Go to [App Name] (unsafe)"
- **"MASTER_SHEET_ID not configured"**: Check your `.env` file and sheet IDs
- **"No clients configured"**: Verify `CLIENT_SHEETS` configuration in `.env`

### **Debug Information:**
- Check backend console for detailed logs
- Use `/api/health` endpoint for system status
- Test individual connections before uploading

## 📚 **Documentation**

- **Setup Guide**: See `setup_guide.md` for detailed setup instructions
- **API Reference**: Check the endpoints above for API usage
- **Configuration**: Review `config.py` for customization options

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License.

## 🆘 **Support**

For issues and questions:
1. Check the troubleshooting section above
2. Review the setup guide
3. Check backend console logs
4. Test API endpoints individually

## 🎉 **Success Indicators**

Your system is working correctly when:
- ✅ Master sheet shows companies with different background colors per client
- ✅ Client sheets contain only their respective data
- ✅ No duplicate companies exist across any sheets
- ✅ Upload progress is tracked in real-time
- ✅ Detailed status messages show processing results 