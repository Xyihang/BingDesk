import { useEffect, useState } from 'react'
import { Button, App, Spin } from 'antd'
import {
  PictureOutlined,
  SyncOutlined,
  CheckCircleOutlined,
  SettingOutlined,
  DesktopOutlined,
  DatabaseOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons'
import { useAppStore } from '../stores/appStore'
import { wallpaperApi } from '../services/api'

export default function Dashboard() {
  const { wallpapers, fetchWallpapers, fetchSystemStatus, systemStatus } = useAppStore()
  const { message } = App.useApp()
  const [loading] = useState(false)
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    fetchWallpapers()
    fetchSystemStatus()
  }, [])

  const handleDownloadAndSet = async () => {
    try {
      setDownloading(true)
      await wallpaperApi.download('uhd', true)
      message.success('壁纸下载并设置成功')
      fetchWallpapers()
      fetchSystemStatus()
    } catch (error) {
      message.error('下载壁纸失败')
    } finally {
      setDownloading(false)
    }
  }

  const isRunning = Boolean(systemStatus?.is_running)

  if (loading) {
    return (
      <div className="page-loading">
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">系统概览</h1>
          <p className="page-subtitle">BingDesk · 必应壁纸桌面管理</p>
        </div>
        <div className="app-status">
          <span
            className="app-status-dot"
            style={{ background: isRunning ? 'var(--color-success)' : 'var(--color-neutral-400)' }}
          />
          {isRunning ? '服务正常运行' : '服务已停止'}
        </div>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <div>
            <div className="stat-label">壁纸数量</div>
            <div className="stat-value">{wallpapers.length} 张</div>
          </div>
          <span className="stat-icon">
            <PictureOutlined />
          </span>
        </div>

        <div className="stat-card">
          <div>
            <div className="stat-label">自动切换</div>
            <div className={`stat-value ${isRunning ? 'is-success' : 'is-error'}`}>
              {isRunning ? '运行中' : '已停止'}
            </div>
          </div>
          <span className="stat-icon">
            {isRunning ? <CheckCircleOutlined /> : <SettingOutlined />}
          </span>
        </div>
      </div>

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">
            <SyncOutlined />
            <span>快捷操作</span>
          </div>
        </div>

        <div className="stack">
          <Button
            type="primary"
            size="large"
            icon={<SyncOutlined spin={downloading} />}
            loading={downloading}
            onClick={handleDownloadAndSet}
          >
            下载并设置新壁纸
          </Button>

          <div className="setting-row" style={{ marginTop: 0 }}>
            <div className="setting-main">
              <span className="setting-name">开机自启</span>
            </div>
            <span
              className="setting-value"
              style={{
                color: systemStatus?.auto_start
                  ? 'var(--color-success)'
                  : 'var(--color-neutral-500)',
              }}
            >
              {systemStatus?.auto_start ? '已启用' : '已禁用'}
            </span>
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">
            <DesktopOutlined />
            <span>系统信息</span>
          </div>
        </div>

        <div className="info-grid">
          <div className="info-item">
            <span className="info-icon">
              <DesktopOutlined />
            </span>
            <div>
              <div className="info-label">应用名称</div>
              <div className="info-value">{systemStatus?.app_name || '加载中...'}</div>
            </div>
          </div>

          <div className="info-item">
            <span className="info-icon">
              <DatabaseOutlined />
            </span>
            <div>
              <div className="info-label">版本</div>
              <div className="info-value">{systemStatus?.version || '加载中...'}</div>
            </div>
          </div>

          <div className="info-item">
            <span className="info-icon">
              <DatabaseOutlined />
            </span>
            <div>
              <div className="info-label">数据库大小</div>
              <div className="info-value">{systemStatus?.database_size || '加载中...'}</div>
            </div>
          </div>

          <div className="info-item">
            <span className="info-icon">
              <PictureOutlined />
            </span>
            <div>
              <div className="info-label">当前壁纸</div>
              <div className="info-value">
                {systemStatus?.current_wallpaper ? '已设置' : '未设置'}
              </div>
            </div>
          </div>

          <div className="info-item">
            <span className="info-icon">
              <PictureOutlined />
            </span>
            <div>
              <div className="info-label">壁纸总数</div>
              <div className="info-value">{systemStatus?.wallpaper_count ?? 0} 张</div>
            </div>
          </div>

          <div className="info-item">
            <span className="info-icon">
              <ClockCircleOutlined />
            </span>
            <div>
              <div className="info-label">下次切换</div>
              <div className="info-value">
                {systemStatus?.next_change_time
                  ? new Date(systemStatus.next_change_time).toLocaleTimeString()
                  : '未设置'}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
