import axios from 'axios';

// API Configuration
const API_BASE_URL = 'https://jj6skt98b3.execute-api.us-east-1.amazonaws.com/dev';

export const apiConfig = {
  baseURL: API_BASE_URL,
  endpoints: {
    intentMapper: '/intent-mapper',
    addProcedure: '/add-doctor-procedure',
    getQuote: '/get-quote',
    showHistory: '/show-history'
  }
};

// API Client

class APIClient {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      }
    });
  }

  // Chat with Bedrock Agent
  async chatWithAgent(message, sessionId = 'frontend-session', conversationHistory = []) {
    try {
      const response = await this.client.post('/intent-mapper', {
        text: message,
        sessionId: sessionId,
        conversationHistory: conversationHistory
      });
      return response.data;
    } catch (error) {
      console.error('Chat error:', error);
      throw this.handleError(error);
    }
  }

  // Direct API calls (bypass Bedrock Agent for faster responses)
  async addProcedure(procedureData) {
    try {
      const response = await this.client.post('/add-doctor-procedure', procedureData);
      return response.data;
    } catch (error) {
      console.error('Add procedure error:', error);
      throw this.handleError(error);
    }
  }

  async getQuote(doctorName, procedureCode) {
    try {
      const response = await this.client.get(`/get-quote?doctorName=${encodeURIComponent(doctorName)}&procedureCode=${encodeURIComponent(procedureCode)}`);
      return response.data;
    } catch (error) {
      console.error('Get quote error:', error);
      throw this.handleError(error);
    }
  }

  async getHistory(doctorName, limit = 5) {
    try {
      const response = await this.client.get(`/show-history?doctorName=${encodeURIComponent(doctorName)}&limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Get history error:', error);
      throw this.handleError(error);
    }
  }

  handleError(error) {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.message || 'Server error occurred';
      return new Error(`${error.response.status}: ${message}`);
    } else if (error.request) {
      // Network error
      return new Error('Network error - please check your connection');
    } else {
      // Other error
      return new Error(error.message || 'An unexpected error occurred');
    }
  }
}

export const apiClient = new APIClient();
