// frontend/src/services/api.js
// ─────────────────────────────────────────────────────────
// All API calls in one place.
// If the backend URL ever changes, we only update it here.
// ─────────────────────────────────────────────────────────

import axios from 'axios';

const BASE_URL = 'https://quintin-jointured-kale.ngrok-free.dev/api';

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


// ── STREAMING FUNCTION (NEW) ─────────────────────────────
// Stream an answer token by token
// onToken  → called with each word/token
// onDone   → called at the end with sources
export const streamQuery = async (
  question,
  role,
  conversationHistory = [],
  onToken,
  onDone
) => {
  const response = await fetch(`${BASE_URL}/stream`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      role,
      n_results:            5,
      conversation_history: conversationHistory
    })
  });

  if (!response.body) {
    throw new Error("Streaming not supported by browser");
  }

  const reader  = response.body.getReader();
  const decoder = new TextDecoder();

  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    // Decode chunk and append to buffer
    buffer += decoder.decode(value, { stream: true });

    // Split into lines
    const lines = buffer.split('\n');

    // Keep last incomplete line in buffer
    buffer = lines.pop();

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;

      try {
        const json = JSON.parse(line.replace('data: ', ''));

        if (json.done) {
          onDone(json.sources || []);
        } else if (json.token) {
          onToken(json.token);
        }
      } catch (err) {
        // Ignore malformed chunks
      }
    }
  }
};