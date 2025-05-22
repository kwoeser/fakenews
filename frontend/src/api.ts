import axios from 'axios';

// Use the proxy path in development mode or environment variables in production
const API_URL = import.meta.env.PROD ? (import.meta.env.VITE_API_URL || 'http://localhost:8000'): '/api';  // Using the proxy path
const API_TIMEOUT = import.meta.env.VITE_API_TIMEOUT ? Number(import.meta.env.VITE_API_TIMEOUT) : 30000;

const api = axios.create({
  baseURL: API_URL,
  timeout: API_TIMEOUT,
});

export const checkNews = async(text: string) => {
  try {
    const response = await api.post('/predict', {text});
    return response.data;
  } catch (error) {
    console.log('Error with calling predict endpoint:', error);
    throw error;
  }
}

export const checkNewsUrl = async(url: string) => {
  try {
    const response = await api.post('/analyze-url', {url});
    return response.data;
  } catch (error) {
    console.log('Error with calling the analyze-url endpoint:', error);
    throw error;
  }
}

export default api; 