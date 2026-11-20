import { useEffect, useState } from 'react'
import { Button, App, Spin, Tag, Modal } from 'antd'
import {
  DownloadOutlined,
  DeleteOutlined,
  PictureOutlined,
  CheckCircleOutlined,
  EyeOutlined,
  DesktopOutlined,
  ClearOutlined,
} from '@ant-design/icons'
import { useAppStore } from '../stores/appStore'
import { wallpaperApi } from '../services/api'
import type { Wallpaper } from '../types'

export default function Wallpapers() {
  const { message, modal } = App.useApp()
  const { wallpapers, fetchWallpapers, fetchSystemStatus } = useAppStore()
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [selectedWallpaper, setSelectedWallpaper] = useState<Wallpaper | null>(null)

  useEffect(() => {
    loadWallpapers()
  }, [])

  const loadWallpapers = async () => {
    setLoading(true)
    await fetchWallpapers()
    setLoading(false)
  }

  const handleDownload = async (setAsWallpaper = false) => {
    try {
      setDownloading(true)
      await wallpaperApi.download('uhd', setAsWallpaper)
      message.success(setAsWallpaper ? '壁纸下载并设置成功' : '壁纸下载成功')
      await loadWallpapers()
      await fetchSystemStatus()
    } catch (error) {
      message.error('下载壁纸失败')
    } finally {
      setDownloading(false)
    }
  }

  const handleSetWallpaper = async (id: number) => {
    try {
      await wallpaperApi.setAsWallpaper(id)
      message.success('壁纸设置成功')
      await loadWallpapers()
      await fetchSystemStatus()
    } catch (error) {
      message.error('设置壁纸失败')
    }
  }

  const handleDelete = async (id: number) => {
    modal.confirm({
      title: '确认删除',
      content: '确定要删除这张壁纸吗？此操作不可恢复。',
      okText: '删除',
      cancelText: '取消',
      okType: 'danger',
      onOk: async () => {
        try {
          await wallpaperApi.delete(id)
          message.success('壁纸删除成功')
          await loadWallpapers()
        } catch (error) {
          message.error('删除壁纸失败')
        }
      },
    })
  }

  const handleDeleteAllExceptCurrent = async () => {
    const currentWallpaper = wallpapers.find((w) => w.is_current)
    const nonCurrentCount = wallpapers.filter((w) => !w.is_current).length

    if (nonCurrentCount === 0) {
      message.info('没有可删除的壁纸')
      return
    }

    modal.confirm({
      title: '批量删除壁纸',
      content: (
        <div>
          <p>确定要删除除当前使用外的所有壁纸吗？</p>
          <p>当前壁纸：{currentWallpaper ? `#${currentWallpaper.id}` : '无'}</p>
          <p>将删除 {nonCurrentCount} 张壁纸，此操作不可恢复。</p>
        </div>
      ),
      okText: '确认删除',
      cancelText: '取消',
      okType: 'danger',
      onOk: async () => {
        try {
          const response = await wallpaperApi.deleteAllExceptCurrent()
          const deletedCount = response.data?.deleted_count ?? 0
          message.success(`成功删除 ${deletedCount} 张壁纸`)
          await loadWallpapers()
          await fetchSystemStatus()
        } catch (error: any) {
          const errorMsg = error.response?.data?.detail || error.message || '批量删除壁纸失败'
          message.error(errorMsg)
        }
      },
    })
  }

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
          <h1 className="page-title">壁纸管理</h1>
          <p className="page-subtitle">共 {wallpapers.length} 张壁纸</p>
        </div>
        <div className="toolbar">
          <Button
            icon={<DownloadOutlined />}
            onClick={() => handleDownload(false)}
            loading={downloading}
            size="large"
          >
            下载壁纸
          </Button>
          <Button
            type="primary"
            icon={<PictureOutlined />}
            onClick={() => handleDownload(true)}
            loading={downloading}
            size="large"
          >
            下载并设置
          </Button>
          {wallpapers.length > 0 && (
            <Button
              danger
              icon={<ClearOutlined />}
              onClick={handleDeleteAllExceptCurrent}
              size="large"
              disabled={wallpapers.filter((w) => !w.is_current).length === 0}
            >
              一键清理
            </Button>
          )}
        </div>
      </div>

      {wallpapers.length === 0 ? (
        <div className="empty-state">
          <PictureOutlined className="empty-icon" />
          <span className="empty-text">还没有壁纸，点击下方按钮下载</span>
          <Button
            type="primary"
            icon={<DownloadOutlined />}
            onClick={() => handleDownload(true)}
            size="large"
          >
            立即下载
          </Button>
        </div>
      ) : (
        <div className="wallpaper-grid">
          {wallpapers.map((wallpaper) => (
            <article className="wallpaper-card" key={wallpaper.id}>
              <div
                className="wallpaper-thumb"
                onClick={() => setSelectedWallpaper(wallpaper)}
              >
                <img
                  src={`/api/wallpapers/${wallpaper.id}/image?width=400`}
                  alt={`壁纸 #${wallpaper.id}`}
                  loading="lazy"
                  onError={(e) => {
                    e.currentTarget.style.visibility = 'hidden'
                  }}
                />

                {wallpaper.is_current && (
                  <span className="thumb-badge">
                    <Tag color="success" icon={<CheckCircleOutlined />}>
                      当前壁纸
                    </Tag>
                  </span>
                )}

                <div className="thumb-actions">
                  <Button
                    shape="circle"
                    icon={<EyeOutlined />}
                    onClick={(e) => {
                      e.stopPropagation()
                      setSelectedWallpaper(wallpaper)
                    }}
                  />
                  {!wallpaper.is_current && (
                    <Button
                      shape="circle"
                      icon={<DesktopOutlined />}
                      onClick={(e) => {
                        e.stopPropagation()
                        handleSetWallpaper(wallpaper.id)
                      }}
                    />
                  )}
                </div>
              </div>

              <div className="wallpaper-body">
                <span className="wallpaper-title">壁纸 #{wallpaper.id}</span>
                <div className="wallpaper-meta">
                  <span>{wallpaper.download_date}</span>
                  <span>{wallpaper.resolution || '4K'}</span>
                </div>
                <div className="wallpaper-actions">
                  <Button
                    icon={<DesktopOutlined />}
                    onClick={() => handleSetWallpaper(wallpaper.id)}
                    disabled={wallpaper.is_current}
                  >
                    {wallpaper.is_current ? '使用中' : '设为壁纸'}
                  </Button>
                  <Button
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => handleDelete(wallpaper.id)}
                    disabled={wallpaper.is_current}
                  />
                </div>
              </div>
            </article>
          ))}
        </div>
      )}

      <Modal
        open={!!selectedWallpaper}
        onCancel={() => setSelectedWallpaper(null)}
        footer={null}
        width={800}
        title={
          <div className="panel-title">
            <PictureOutlined />
            <span>壁纸详情</span>
          </div>
        }
      >
        {selectedWallpaper && (
          <div>
            <div className="detail-image">
              <img
                src={`/api/wallpapers/${selectedWallpaper.id}/image`}
                alt={`壁纸 #${selectedWallpaper.id}`}
              />
            </div>

            <div className="detail-grid">
              <div className="detail-item">
                <div className="detail-label">文件路径</div>
                <div className="detail-value">{selectedWallpaper.file_path}</div>
              </div>
              <div className="detail-item">
                <div className="detail-label">分辨率</div>
                <div className="detail-value">{selectedWallpaper.resolution || '未知'}</div>
              </div>
              <div className="detail-item">
                <div className="detail-label">下载日期</div>
                <div className="detail-value">{selectedWallpaper.download_date}</div>
              </div>
              <div className="detail-item">
                <div className="detail-label">状态</div>
                <div className="detail-value">
                  <Tag color={selectedWallpaper.is_current ? 'success' : 'default'}>
                    {selectedWallpaper.is_current ? '当前壁纸' : '未使用'}
                  </Tag>
                </div>
              </div>
            </div>

            <div className="wallpaper-actions">
              <Button
                type="primary"
                icon={<DesktopOutlined />}
                size="large"
                onClick={() => {
                  handleSetWallpaper(selectedWallpaper.id)
                  setSelectedWallpaper(null)
                }}
                disabled={selectedWallpaper.is_current}
                block
              >
                {selectedWallpaper.is_current ? '当前正在使用' : '设为桌面壁纸'}
              </Button>
              <Button
                danger
                icon={<DeleteOutlined />}
                size="large"
                onClick={() => {
                  handleDelete(selectedWallpaper.id)
                  setSelectedWallpaper(null)
                }}
                disabled={selectedWallpaper.is_current}
              >
                删除
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
