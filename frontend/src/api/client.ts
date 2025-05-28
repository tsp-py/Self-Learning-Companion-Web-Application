import axios from 'axios';
import Cookies from 'js-cookie';
import type { User, File, LearningPath, ReadingSession, Stats } from '../types';

const API_URL = 'http://localhost:5000/api';

const client = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth API
export const auth = {
  login: async (email: string, password: string) => {
    const response = await client.post('/auth/login', { email, password });
    return response.data;
  },
  logout: async () => {
    const response = await client.post('/auth/logout');
    return response.data;
  },
  getCurrentUser: async () => {
    const response = await client.get('/auth/me');
    return response.data.user as User;
  },
};

// Files API
export const files = {
  upload: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await client.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.file as File;
  },
  list: async () => {
    const response = await client.get('/files');
    return response.data.files as File[];
  },
  get: async (id: number) => {
    const response = await client.get(`/files/${id}`);
    return response.data.file as File;
  },
};

// Learning Paths API
export const paths = {
  create: async (path: { title: string; description: string; resources: number[] }) => {
    const response = await client.post('/paths', path);
    return response.data.path as LearningPath;
  },
  list: async () => {
    const response = await client.get('/paths');
    return response.data.paths as LearningPath[];
  },
  get: async (id: number) => {
    const response = await client.get(`/paths/${id}`);
    return response.data.path as LearningPath;
  },
  completeResource: async (pathId: number, resourceId: number) => {
    const response = await client.post(`/paths/${pathId}/resources/${resourceId}/complete`);
    return response.data.resource;
  },
};

// Time Tracking API
export const tracking = {
  startSession: async (fileId: number) => {
    const response = await client.post('/tracking/start', { file_id: fileId });
    return response.data.session as ReadingSession;
  },
  endSession: async (logId: number) => {
    const response = await client.post('/tracking/end', { log_id: logId });
    return response.data.session as ReadingSession;
  },
  getStats: async () => {
    const response = await client.get('/tracking/stats');
    return response.data as Stats;
  },
}; 