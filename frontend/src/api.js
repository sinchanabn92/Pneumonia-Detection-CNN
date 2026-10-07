import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Accept': 'application/json',
  },
});

export const getHealth = async () => {
  const res = await client.get('/health');
  return res.data;
};

export const getModelInfo = async () => {
  const res = await client.get('/model-info');
  return res.data;
};

export const predictXray = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await client.post('/predict', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return res.data;
};

export const getHistory = async (page = 1, pageSize = 20) => {
  const res = await client.get('/history', {
    params: { page, page_size: pageSize },
  });
  return res.data;
};

export const getAnalysisDetail = async (analysisId) => {
  const res = await client.get(`/history/${analysisId}`);
  return res.data;
};

export const getReportUrl = (analysisId) => {
  return `${API_BASE_URL}/report/${analysisId}`;
};

export const getAssetUrl = (path) => {
  if (!path) return '';
  if (path.startsWith('http')) return path;
  return `${API_BASE_URL}${path.startsWith('/') ? '' : '/'}${path}`;
};
