import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

export const health = () => api.get('/health').then((r) => r.data);

export const listDocuments = () => api.get('/documents').then((r) => r.data);
export const uploadDocument = (file, onProgress) => {
  const form = new FormData();
  form.append('file', file);
  return api.post('/documents/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress,
  }).then((r) => r.data);
};
export const getDocument = (id) => api.get(`/documents/${id}`).then((r) => r.data);
export const deleteDocument = (id) => api.delete(`/documents/${id}`).then((r) => r.data);
export const reindexDocument = (id) => api.post(`/documents/${id}/reindex`).then((r) => r.data);

export const askQuestion = (payload) => api.post('/chat', payload).then((r) => r.data);
export const listSessions = () => api.get('/chat/sessions').then((r) => r.data);
export const getSession = (id) => api.get(`/chat/sessions/${id}`).then((r) => r.data);
export const deleteSession = (id) => api.delete(`/chat/sessions/${id}`).then((r) => r.data);

export const runEvaluation = (payload) => api.post('/evaluation/run', payload).then((r) => r.data);
export const listEvalRuns = () => api.get('/evaluation/runs').then((r) => r.data);
export const getEvalRun = (id) => api.get(`/evaluation/runs/${id}`).then((r) => r.data);

export default api;
