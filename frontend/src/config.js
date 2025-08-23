// Configuration file for environment variables
const config = {
  // API Configuration
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000',
  
  // App Configuration
  APP_NAME: import.meta.env.VITE_APP_NAME || 'Crunchbase Automation',
  
  // Environment
  IS_DEVELOPMENT: import.meta.env.DEV,
  IS_PRODUCTION: import.meta.env.PROD,
  
  // API Endpoints
  ENDPOINTS: {
    CLIENTS: '/api/clients',
    UPLOAD: '/api/upload',
    STATUS: '/api/status',
    HEALTH: '/api/health',
    TEST_MASTER: '/api/test-master-connection',
    TEST_CLIENT: '/api/test-client-connection',
    COLUMN_MAPPING: '/api/column-mapping'
  }
}

// Helper function to build full API URLs
config.buildApiUrl = (endpoint) => {
  return `${config.API_BASE_URL}${endpoint}`
}

// Helper function to get endpoint URL
config.getEndpoint = (name) => {
  return config.buildApiUrl(config.ENDPOINTS[name])
}

export default config 