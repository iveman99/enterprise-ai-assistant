// frontend/src/services/api.js
// ─────────────────────────────────────────────────────────
// All API calls in one place.
// If the backend URL ever changes, we only update it here.
// ─────────────────────────────────────────────────────────

import axios from 'axios';

const BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' }
});


// Send a question and get an answer
export const queryDocuments = async (
  question,
  role,
  conversationHistory = [],
  nResults = 5
) => {
  const response = await api.post('/query', {
    question,
    role,
    n_results:            nResults,
    conversation_history: conversationHistory
  });
  return response.data;
};


// Get system stats (doc count, chunk count)
export const getStats = async () => {
  const response = await api.get('/stats');
  return response.data;
};


// Get all available roles
export const getRoles = async () => {
  const response = await api.get('/roles');
  return response.data;
};


// Health check
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};