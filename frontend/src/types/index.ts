export interface Wallpaper {
  id: number
  file_path: string
  source_url: string | null
  resolution: string | null
  download_date: string
  is_current: boolean
  created_at: string
}

export interface Setting {
  id: number
  key: string
  value: string
  description: string | null
  updated_at: string
}

export interface SystemStatus {
  app_name: string
  version: string
  is_running: boolean
  auto_start: boolean
  current_wallpaper: string | null
  next_change_time: string | null
  database_size: string
  wallpaper_count: number
}

export interface TarotCard {
  name: string
  reversed: boolean
  meaning?: string
  upright_meaning?: string
  reversed_meaning?: string
}

export interface TarotReading {
  spread_type: string
  cards: TarotCard[]
  ai_interpretation?: string
}

export interface TarotHistoryItem {
  id: number
  reading_type: string
  question?: string
  period_months?: number
  cards: TarotCard[]
  ai_interpretation?: string
  overall_fortune?: string
  created_at: string
}

export interface TarotHistoryData {
  total: number
  page: number
  page_size: number
  items: TarotHistoryItem[]
}

export interface ApiResponse<T> {
  total?: number
  items?: T[]
  message?: string
  data?: T
}
