import { create } from 'zustand'
import type { Wallpaper, Setting, SystemStatus } from '../types'
import { wallpaperApi, settingsApi, systemApi } from '../services/api'

interface AppState {
  wallpapers: Wallpaper[]
  settings: Setting[]
  systemStatus: SystemStatus | null
  loading: boolean
  error: string | null
  
  fetchWallpapers: () => Promise<void>
  fetchSettings: () => Promise<void>
  fetchSystemStatus: () => Promise<void>
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useAppStore = create<AppState>((set) => ({
  wallpapers: [],
  settings: [],
  systemStatus: null,
  loading: false,
  error: null,

  fetchWallpapers: async () => {
    try {
      set({ loading: true, error: null })
      const response = await wallpaperApi.getAll()
      set({ 
        wallpapers: response.data.items || [], 
        loading: false 
      })
    } catch (error) {
      set({ 
        error: '获取壁纸列表失败', 
        loading: false 
      })
    }
  },

  fetchSettings: async () => {
    try {
      set({ loading: true, error: null })
      const response = await settingsApi.getAll()
      set({ 
        settings: response.data.items || [], 
        loading: false 
      })
    } catch (error) {
      set({ 
        error: '获取配置失败', 
        loading: false 
      })
    }
  },

  fetchSystemStatus: async () => {
    try {
      const response = await systemApi.getStatus()
      set({ systemStatus: response.data })
    } catch (error) {
      console.error('Failed to fetch system status:', error)
      set({ error: '获取系统状态失败' })
    }
  },

  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}))
