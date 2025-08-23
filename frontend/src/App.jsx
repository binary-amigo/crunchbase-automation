import { useState, useCallback, useEffect } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [status, setStatus] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const [processingId, setProcessingId] = useState(null)
  const [processingStatus, setProcessingStatus] = useState(null)
  const [progress, setProgress] = useState(0)
  const [clients, setClients] = useState([])
  const [selectedClient, setSelectedClient] = useState('')
  const [isLoadingClients, setIsLoadingClients] = useState(true)

  // Load available clients on component mount
  useEffect(() => {
    loadAvailableClients()
  }, [])

  const loadAvailableClients = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/clients')
      if (response.ok) {
        const result = await response.json()
        setClients(result.clients || [])
        if (result.clients && result.clients.length > 0) {
          setSelectedClient(result.clients[0].id)
        }
      } else {
        console.error('Failed to load clients')
        setStatus('Failed to load available clients')
      }
    } catch (error) {
      console.error('Error loading clients:', error)
      setStatus('Error loading clients. Please check if the backend is running.')
    } finally {
      setIsLoadingClients(false)
    }
  }

  const handleDrag = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile.type === 'text/csv' || droppedFile.name.endsWith('.csv')) {
        setFile(droppedFile)
        setStatus('')
        setProcessingId(null)
        setProcessingStatus(null)
        setProgress(0)
      } else {
        setStatus('Please select a valid CSV file')
      }
    }
  }, [])

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      if (selectedFile.type === 'text/csv' || selectedFile.name.endsWith('.csv')) {
        setFile(selectedFile)
        setStatus('')
        setProcessingId(null)
        setProcessingStatus(null)
        setProgress(0)
      } else {
        setStatus('Please select a valid CSV file')
      }
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setStatus('Please select a file first')
      return
    }

    if (!selectedClient) {
      setStatus('Please select a client first')
      return
    }

    setIsUploading(true)
    setStatus('Uploading CSV file...')
    setProgress(10)

    try {
      // Create FormData for file upload
      const formData = new FormData()
      formData.append('file', file)
      formData.append('client_id', selectedClient)

      // Send to Flask backend
      const response = await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        body: formData
      })
      
      if (response.ok) {
        const result = await response.json()
        setProcessingId(result.processing_id)
        setStatus('File uploaded! Processing CSV and updating Google Sheets...')
        setProgress(30)
        
        // Start polling for status updates
        pollProcessingStatus(result.processing_id)
      } else {
        const error = await response.json()
        setStatus(error.error || 'Upload failed. Please try again.')
        setProgress(0)
      }
    } catch (error) {
      console.error('Upload error:', error)
      setStatus('Upload failed. Please check if the backend is running.')
      setProgress(0)
    } finally {
      setIsUploading(false)
    }
  }

  const pollProcessingStatus = async (filename) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:5000/api/status/${filename}`)
        if (response.ok) {
          const statusData = await response.json()
          setProcessingStatus(statusData)
          
          // Update progress based on status
          if (statusData.progress) {
            setProgress(30 + (statusData.progress * 0.7)) // 30% to 100%
          }
          
          // Update status message
          if (statusData.status === 'processing') {
            setStatus(statusData.message)
          } else if (statusData.status === 'completed') {
            setStatus(statusData.message)
            setProgress(100)
            clearInterval(pollInterval)
            setIsUploading(false)
          } else if (statusData.status === 'failed') {
            setStatus(`Error: ${statusData.message}`)
            setProgress(0)
            clearInterval(pollInterval)
            setIsUploading(false)
          } else if (statusData.status === 'warning') {
            setStatus(statusData.message)
            setProgress(100)
            clearInterval(pollInterval)
            setIsUploading(false)
          }
        }
      } catch (error) {
        console.error('Status polling error:', error)
        clearInterval(pollInterval)
      }
    }, 2000) // Poll every 2 seconds

    // Stop polling after 5 minutes (300 seconds) to prevent infinite polling
    setTimeout(() => {
      clearInterval(pollInterval)
      if (isUploading) {
        setStatus('Processing timeout. Please check the backend logs.')
        setIsUploading(false)
      }
    }, 300000)
  }

  const removeFile = () => {
    setFile(null)
    setStatus('')
    setProcessingId(null)
    setProcessingStatus(null)
    setProgress(0)
  }

  const getStatusIcon = () => {
    if (isUploading) {
      return (
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-3"></div>
      )
    }
    
    if (processingStatus?.status === 'completed') {
      return (
        <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    }
    
    if (processingStatus?.status === 'failed') {
      return (
        <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    }
    
    if (processingStatus?.status === 'warning') {
      return (
        <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      )
    }
    
    return (
      <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  }

  const getStatusColor = () => {
    if (processingStatus?.status === 'completed') return 'text-green-800'
    if (processingStatus?.status === 'failed') return 'text-red-800'
    if (processingStatus?.status === 'warning') return 'text-yellow-800'
    return 'text-blue-800'
  }

  const getSelectedClientName = () => {
    const client = clients.find(c => c.id === selectedClient)
    return client ? client.name : 'Unknown Client'
  }

  const handleClientChange = (clientId) => {
    setSelectedClient(clientId)
    // Reset file input when client changes
    setFile(null)
    setDragActive(false)
    setStatus('')
    setProcessingStatus(null)
    setProgress(0)
    // Clear the file input element
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            CSV File Upload
          </h1>
          <p className="text-gray-600">
            Upload your CSV file and we'll process it for you
          </p>
        </div>

        {/* Client Selection */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Select Client</h2>
          {isLoadingClients ? (
            <div className="flex items-center justify-center py-4">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-3"></div>
              <span className="text-gray-600">Loading clients...</span>
            </div>
          ) : (
            <div className="space-y-3">
              {clients.map((client) => (
                <label key={client.id} className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="radio"
                    name="client"
                    value={client.id}
                    checked={selectedClient === client.id}
                    onChange={(e) => handleClientChange(e.target.value)}
                    className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500"
                  />
                  <div>
                    <span className="font-medium text-gray-900">{client.name}</span>
                    <span className="text-sm text-gray-500 ml-2">({client.sheet_name})</span>
                  </div>
                </label>
              ))}
            </div>
          )}
          {clients.length === 0 && !isLoadingClients && (
            <p className="text-red-600 text-sm">No clients configured. Please check your backend configuration.</p>
          )}
        </div>

        {/* Upload Area */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <div
            className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 ${
              dragActive 
                ? 'border-blue-400 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {!file ? (
              <div>
                <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <p className="text-lg font-medium text-gray-900 mb-2">
                  Drop your CSV file here
                </p>
                <p className="text-gray-500 mb-4">
                  or click to browse files
                </p>
                <label className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 cursor-pointer transition-colors">
                  Choose File
                  <input
                    type="file"
                    accept=".csv,text/csv"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </label>
              </div>
            ) : (
              <div>
                <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <p className="text-lg font-medium text-gray-900 mb-2">
                  File Selected
                </p>
                <p className="text-gray-500 mb-4">
                  {file.name} ({(file.size / 1024).toFixed(1)} KB)
                </p>
                <div className="flex gap-3 justify-center">
                  <button
                    onClick={removeFile}
                    disabled={isUploading}
                    className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Remove
                  </button>
                  <button
                    onClick={handleUpload}
                    disabled={isUploading || !selectedClient}
                    className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {isUploading ? 'Processing...' : 'Upload File'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        {isUploading && progress > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
            <div className="mb-4">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Processing Progress</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>
            <div className="text-center text-sm text-gray-600">
              {progress < 30 && 'Uploading file...'}
              {progress >= 30 && progress < 100 && 'Processing CSV and updating Google Sheets...'}
              {progress === 100 && 'Complete!'}
            </div>
          </div>
        )}

        {/* Status and Loading */}
        {status && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                {getStatusIcon()}
                <span className={`font-medium ${getStatusColor()}`}>
                  {status}
                </span>
              </div>
              {isUploading && (
                <div className="text-sm text-gray-500">
                  Please wait...
                </div>
              )}
            </div>
            
            {/* Show detailed processing info when available */}
            {processingStatus && processingStatus.data_info && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Processing Details:</h4>
                <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                  <div>
                    <span className="font-medium">Client:</span> {getSelectedClientName()}
                  </div>
                  <div>
                    <span className="font-medium">Rows processed:</span> {processingStatus.data_info.rows}
                  </div>
                  <div>
                    <span className="font-medium">Columns mapped:</span> {processingStatus.data_info.columns}
                  </div>
                  <div>
                    <span className="font-medium">File size:</span> {processingStatus.data_info.file_size_mb} MB
                  </div>
                  <div>
                    <span className="font-medium">Status:</span> {processingStatus.status}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default App
