import axios from 'axios'
import type { Wallpaper, Setting, SystemStatus, ApiResponse } from '../types'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

const tarotAxios = axios.create({
  baseURL: '/api',
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const wallpaperApi = {
  getAll: (skip = 0, limit = 100) => 
    api.get<ApiResponse<Wallpaper>>('/wallpapers', { params: { skip, limit } }),
  getCurrent: () => api.get<Wallpaper>('/wallpapers/current'),
  download: (quality = 'uhd', setAsWallpaper = false) =>
    api.post<Wallpaper>('/wallpapers/download', null, {
      params: { quality, set_as_wallpaper: setAsWallpaper },
    }),
  setAsWallpaper: (id: number) => api.post(`/wallpapers/${id}/set`),
  delete: (id: number) => api.delete(`/wallpapers/${id}`),
  deleteAllExceptCurrent: () => api.delete('/wallpapers/batch/all-except-current'),
}

export const settingsApi = {
  getAll: () => api.get<ApiResponse<Setting>>('/settings'),
  get: (key: string) => api.get<Setting>(`/settings/${key}`),
  update: (key: string, value: string, description?: string) =>
    api.put<Setting>(`/settings/${key}`, { value, description }),
  batchUpdate: (settings: { key: string; value: string; description?: string }[]) =>
    api.post('/settings/batch', settings),
  init: () => api.post('/settings/init'),
}

export const systemApi = {
  getStatus: () => api.get<SystemStatus>('/system/status'),
  setAutostart: (enabled: boolean) =>
    api.post('/system/autostart', null, { params: { enabled } }),
  getAutostart: () => api.get<{ enabled: boolean }>('/system/autostart'),
  getAutostartScripts: () => api.get<{ bat: string; powershell: string; bat_hidden: string; powershell_hidden: string }>('/system/autostart/scripts'),
  startScheduler: (interval: number) =>
    api.post('/system/scheduler/start', null, { params: { interval } }),
  stopScheduler: () => api.post('/system/scheduler/stop'),
  getLogs: (lines = 100) => api.get('/system/logs', { params: { lines } }),
  stopServices: () => api.post<{ success: boolean; message: string; processes: string[] }>('/system/services/stop'),
}

export const authApi = {
  verify: (password: string, type: 'app' | 'grid') =>
    api.post<{ valid: boolean }>('/auth/verify', { password, type }),
  changePassword: (currentPassword: string, newPassword: string, type: 'app' | 'grid') =>
    api.put<{ success: boolean; message: string }>('/auth/password', {
      current_password: currentPassword,
      new_password: newPassword,
      type,
    }),
}

interface TarotApiResponse {
  success: boolean
  data: any
  message: string
}

export const tarotApi = {
  getReading: (months: number, question?: string) =>
    tarotAxios.post<TarotApiResponse>('/tarot/reading', { months, question }),
  getDaily: () => tarotAxios.get<TarotApiResponse>('/tarot/daily'),
  getCelticCross: () => tarotAxios.get<TarotApiResponse>('/tarot/celtic-cross'),
  getCards: () => tarotAxios.get<TarotApiResponse>('/tarot/cards'),
  getHistory: (page = 1, pageSize = 20, readingType?: string) => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) })
    if (readingType) params.set('reading_type', readingType)
    return tarotAxios.get<TarotApiResponse>(`/tarot/history?${params}`)
  },
  getHistoryDetail: (id: number) =>
    tarotAxios.get<TarotApiResponse>(`/tarot/history/${id}`),
  deleteHistory: (id: number) =>
    tarotAxios.delete<TarotApiResponse>(`/tarot/history/${id}`),
}

export default api
