# CSV Upload & Master Sheet Backend Setup Guide

This guide will help you set up the CSV upload backend with Google Sheets integration, featuring a master sheet for global duplicate prevention and separate client sheets for data isolation.

## 🏗️ **System Architecture**

### **Master Sheet (Global Registry)**
- **Purpose**: Prevents duplicate companies across all clients
- **Columns**: Client Name, Company, Date Added
- **Background Colors**: Different colors for each client for visual separation

### **Client Sheets (Data Storage)**
- **Purpose**: Store full CSV data for each client separately
- **Structure**: Your existing sheet columns (Date, Source, Campaign, Company Name, etc.)
- **Isolation**: Each client only sees their own data

## 📋 **Prerequisites**

1. **Python 3.8+** installed on your system
2. **Google Cloud Project** with Google Sheets API enabled
3. **OAuth 2.0 credentials** for Google Sheets API
4. **Three Google Sheets**:
   - Master Sheet (for company registry)
   - Client A Sheet (for Client A data)
   - Client B Sheet (for Client B data)

## 🔧 **Step 1: Google Cloud Project Setup**

### **1.1 Create Google Cloud Project**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: `Crunchbase Automation`
4. Click "Create"

### **1.2 Enable Google Sheets API**
1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on it and click "Enable"

### **1.3 Create OAuth 2.0 Credentials**
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. **IMPORTANT**: Choose "Desktop application" (NOT web application)
4. Enter name: `Crunchbase Automation Desktop`
5. Click "Create"
6. Download the JSON file and rename it to `credentials.json`
7. Place it in the `backend/` folder

### **1.4 Create Consent Screen (if prompted)**
1. If asked to create consent screen, choose "External"
2. Fill in required fields:
   - App name: `Crunchbase Automation`
   - User support email: Your email
   - Developer contact email: Your email
3. Add scopes: `https://www.googleapis.com/auth/spreadsheets`
4. Add test users: Your email address

## 📊 **Step 2: Create Google Sheets**

### **2.1 Master Sheet (Company Registry)**
1. Create a new Google Sheet
2. Name it: `Master Company Registry`
3. Add headers in row 1:
   - Column A: `Client Name`
   - Column B: `Company`
   - Column C: `Date Added`
4. Copy the Sheet ID from the URL

### **2.2 Client A Sheet**
1. Create a new Google Sheet
2. Name it: `Client A Data`
3. Add your existing headers (Date, Source, Campaign, Company Name, etc.)
4. Copy the Sheet ID from the URL

### **2.3 Client B Sheet**
1. Create a new Google Sheet
2. Name it: `Client B Data`
3. Add the same headers as Client A
4. Copy the Sheet ID from the URL

## ⚙️ **Step 3: Environment Configuration**

### **3.1 Create .env file**
1. Copy `env.example` to `.env`
2. Fill in your configuration:

```bash
# Google Sheets API Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEETS_TOKEN_FILE=token.json

# Master Sheet (Global Registry for Duplicate Prevention)
MASTER_SHEET_ID=your_master_sheet_id_here
MASTER_SHEET_NAME=Master Registry

# Client A Configuration
CLIENT_A_NAME=Client A
CLIENT_A_SHEET_ID=your_client_a_sheet_id_here
CLIENT_A_SHEET_NAME=Client A Data

# Client B Configuration
CLIENT_B_NAME=Client B
CLIENT_B_SHEET_ID=your_client_b_sheet_id_here
CLIENT_B_SHEET_NAME=Client B Data

# Duplicate Detection Settings
DUPLICATE_HANDLING=skip
DUPLICATE_MIN_MATCH_SCORE=1.0

# Column Mapping and Processing
AUTO_MAP_COLUMNS=true
APPEND_TO_NEXT_ROW=true

# File Upload Settings
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

### **3.2 Get Sheet IDs**
- **Master Sheet ID**: From `https://docs.google.com/spreadsheets/d/YOUR_MASTER_SHEET_ID/edit`
- **Client A Sheet ID**: From `https://docs.google.com/spreadsheets/d/YOUR_CLIENT_A_SHEET_ID/edit`
- **Client B Sheet ID**: From `https://docs.google.com/spreadsheets/d/YOUR_CLIENT_B_SHEET_ID/edit`

## 🚀 **Step 4: Install and Run**

### **4.1 Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

### **4.2 Run the Backend**
```bash
python app.py
```

Or use the convenience script:
```bash
chmod +x run.sh
./run.sh
```

## 🔍 **Step 5: Test the System**

### **5.1 Test Master Sheet Connection**
```bash
curl http://localhost:5000/api/test-master-connection
```

### **5.2 Test Client Sheet Connections**
```bash
curl http://localhost:5000/api/test-client-connection/client_a
curl http://localhost:5000/api/test-client-connection/client_b
```

### **5.3 Get Available Clients**
```bash
curl http://localhost:5000/api/clients
```

### **5.4 Test Column Mapping**
```bash
curl http://localhost:5000/api/column-mapping/client_a
```

## 📱 **Step 6: Frontend Integration**

### **6.1 Start Frontend**
```bash
cd frontend
npm install
npm run dev
```

### **6.2 Upload CSV**
1. Select a client (Client A or Client B)
2. Upload your CSV file
3. Watch real-time progress
4. See detailed results

## 🔄 **How It Works**

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

## 🎯 **Example Scenario**

### **Initial State:**
- **Master Sheet**: Empty
- **Client A Sheet**: Empty
- **Client B Sheet**: Empty

### **Upload CSV for Client A with "XYZ Company":**
- **Master Sheet**: `Client A | XYZ Company | 01/01/24` (Light Blue background)
- **Client A Sheet**: Full CSV row with all data
- **Client B Sheet**: Empty

### **Upload CSV for Client B with "XYZ Company":**
- **Result**: SKIPPED (company already exists in master sheet)
- **Client B Sheet**: No data added

### **Upload CSV for Client B with "ABC Corp":**
- **Master Sheet**: `Client B | ABC Corp | 01/02/24` (Light Green background)
- **Client A Sheet**: Unchanged
- **Client B Sheet**: Full CSV row with ABC Corp data

## 🛠️ **Troubleshooting**

### **Common Issues:**

1. **"Client secrets must be for a web or installed app"**
   - **Solution**: Recreate credentials as "Desktop application"

2. **"Access blocked: App not verified"**
   - **Solution**: Click "Advanced" → "Go to [App Name] (unsafe)"

3. **"MASTER_SHEET_ID not configured"**
   - **Solution**: Check your `.env` file and sheet IDs

4. **"No clients configured"**
   - **Solution**: Verify `CLIENT_SHEETS` configuration in `.env`

### **Debug Information:**
- Check backend console for detailed logs
- Use `/api/health` endpoint for system status
- Test individual connections before uploading

## 📚 **API Endpoints**

- `POST /api/upload` - Upload CSV with client selection
- `GET /api/status/<filename>` - Check processing status
- `GET /api/clients` - Get available clients
- `GET /api/column-mapping/<client_id>` - Get column mapping info
- `GET /api/test-master-connection` - Test master sheet connection
- `GET /api/test-client-connection/<client_id>` - Test client sheet connection
- `GET /api/health` - Health check

## 🎉 **Success!**

Your system is now configured with:
- ✅ **Global duplicate prevention** via master sheet
- ✅ **Client data isolation** in separate sheets
- ✅ **Visual client separation** with background colors
- ✅ **Professional data management** for multiple clients
- ✅ **Real-time progress tracking** and detailed reporting

The system will automatically:
- Prevent duplicate companies across all clients
- Apply appropriate background colors for visual separation
- Maintain clean data isolation between clients
- Provide comprehensive upload status and progress tracking 