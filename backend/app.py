from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from config import Config
from csv_processor import CSVProcessor
from google_sheets_service import GoogleSheetsService
from master_sheet_service import MasterSheetService
import threading
import time

app = Flask(__name__)
CORS(app)

config = Config()
UPLOAD_FOLDER = config.UPLOAD_FOLDER
ALLOWED_EXTENSIONS = config.ALLOWED_EXTENSIONS

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

processing_status = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_csv_and_upload(file_path, filename, client_id):
    global processing_status
    try:
        processing_status[filename] = {'status': 'processing', 'message': 'Processing CSV file...', 'progress': 0}
        
        # Initialize master sheet if needed
        master_service = MasterSheetService()
        master_init_success, master_init_message = master_service.initialize_master_sheet()
        if not master_init_success:
            processing_status[filename] = {'status': 'failed', 'message': f'Master sheet initialization failed: {master_init_message}', 'progress': 0}
            return
        
        processing_status[filename] = {'status': 'processing', 'message': 'Master sheet ready, processing CSV...', 'progress': 20}
        
        csv_processor = CSVProcessor(file_path)
        success, data, message = csv_processor.process_csv()
        if not success:
            processing_status[filename] = {'status': 'failed', 'message': f'CSV processing failed: {message}', 'progress': 0}
            return
        
        processing_status[filename] = {'status': 'processing', 'message': 'CSV processed, checking for duplicates and uploading...', 'progress': 50}
        
        data_info = csv_processor.get_data_info()
        # Validate data
        is_valid, issues = csv_processor.validate_data()
        if not is_valid:
            processing_status[filename] = {'status': 'warning', 'message': f'Data uploaded with warnings: {"; ".join(issues)}', 'progress': 75}
        
        # Create Google Sheets service for the specific client
        sheets_service = GoogleSheetsService(client_id=client_id)
        
        # Get client info for display
        client_info, error = sheets_service.get_client_sheet_info()
        if error:
            processing_status[filename] = {'status': 'failed', 'message': f'Client configuration error: {error}', 'progress': 75}
            return
        
        client_name = client_info['name']
        
        # Upload data to client sheet and update master sheet
        upload_success, upload_message = sheets_service.append_data(data, client_name)
        if upload_success:
            mapping_info = sheets_service.get_column_mapping_info()
            processing_status[filename] = {
                'status': 'completed', 
                'message': f'{upload_message}. Data: {data_info["rows"]} rows, {data_info["columns"]} columns', 
                'progress': 100, 
                'data_info': data_info, 
                'column_mapping': mapping_info,
                'client_name': client_name
            }
        else:
            processing_status[filename] = {'status': 'failed', 'message': f'Upload failed: {upload_message}', 'progress': 75}
            
    except Exception as e:
        processing_status[filename] = {'status': 'failed', 'message': f'Unexpected error: {str(e)}', 'progress': 0}

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    client_id = request.form.get('client_id', 'client_a')  # Default to client_a
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Start background processing
        thread = threading.Thread(
            target=process_csv_and_upload, 
            args=(file_path, filename, client_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'File uploaded successfully. Processing started.', 
            'filename': filename, 
            'status': 'uploaded', 
            'processing_id': filename,
            'client_id': client_id
        }), 200
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/status/<filename>', methods=['GET'])
def get_processing_status(filename):
    global processing_status
    if filename not in processing_status:
        return jsonify({'error': 'File not found'}), 404
    return jsonify(processing_status[filename]), 200

@app.route('/api/clients', methods=['GET'])
def get_available_clients():
    """Get list of available clients"""
    try:
        clients = []
        for client_id, client_info in config.CLIENT_SHEETS.items():
            clients.append({
                'id': client_id,
                'name': client_info['name'],
                'sheet_name': client_info['sheet_name']
            })
        return jsonify({'status': 'success', 'clients': clients}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error getting clients: {str(e)}'}), 500

@app.route('/api/test-master-connection', methods=['GET'])
def test_master_sheet_connection():
    """Test connection to master sheet"""
    try:
        master_service = MasterSheetService()
        success, message = master_service.test_connection()
        if success:
            return jsonify({'status': 'success', 'message': message}), 200
        else:
            return jsonify({'status': 'error', 'message': message}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Master sheet connection test failed: {str(e)}'}), 500

@app.route('/api/test-client-connection/<client_id>', methods=['GET'])
def test_client_sheet_connection(client_id):
    """Test connection to specific client sheet"""
    try:
        if client_id not in config.CLIENT_SHEETS:
            return jsonify({'status': 'error', 'message': f'Unknown client ID: {client_id}'}), 400
        
        sheets_service = GoogleSheetsService(client_id=client_id)
        success, message = sheets_service.test_connection()
        if success:
            return jsonify({'status': 'success', 'message': message}), 200
        else:
            return jsonify({'status': 'error', 'message': message}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Client sheet connection test failed: {str(e)}'}), 500

@app.route('/api/column-mapping/<client_id>', methods=['GET'])
def get_column_mapping_info(client_id):
    """Get column mapping information for a specific client"""
    try:
        if client_id not in config.CLIENT_SHEETS:
            return jsonify({'status': 'error', 'message': f'Unknown client ID: {client_id}'}), 400
        
        sheets_service = GoogleSheetsService(client_id=client_id)
        mapping_info = sheets_service.get_column_mapping_info()
        if mapping_info:
            return jsonify({'status': 'success', 'data': mapping_info}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Could not retrieve column mapping info'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error getting column mapping: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Backend is running'}), 200

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'CSV Upload & Master Sheet Backend API', 
        'endpoints': {
            'upload': '/api/upload (POST) - Upload CSV file with client selection',
            'status': '/api/status/<filename> (GET) - Check processing status',
            'clients': '/api/clients (GET) - Get available clients',
            'column_mapping': '/api/column-mapping/<client_id> (GET) - Get column mapping info',
            'test_master': '/api/test-master-connection (GET) - Test master sheet connection',
            'test_client': '/api/test-client-connection/<client_id> (GET) - Test client sheet connection',
            'health': '/api/health (GET) - Health check'
        }
    }), 200

if __name__ == '__main__':
    print("Starting CSV Upload & Master Sheet Backend...")
    print("Available endpoints:")
    print("  - POST /api/upload - Upload CSV file with client selection")
    print("  - GET  /api/status/<filename> - Check processing status")
    print("  - GET  /api/clients - Get available clients")
    print("  - GET  /api/column-mapping/<client_id> - Get column mapping info")
    print("  - GET  /api/test-master-connection - Test master sheet connection")
    print("  - GET  /api/test-client-connection/<client_id> - Test client sheet connection")
    print("  - GET  /api/health - Health check")
    print("  - GET  / - API information")
    print("\nBackend will be available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 