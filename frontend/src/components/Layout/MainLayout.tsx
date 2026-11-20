import { ReactNode, useState } from 'react'
import { Layout, Menu } from 'antd'
import {
  DashboardOutlined,
  PictureOutlined,
  SettingOutlined,
  StarOutlined,
} from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'

const { Sider, Header, Content } = Layout

const menuItems = [
  {
    key: '/dashboard',
    icon: <DashboardOutlined />,
    label: '仪表盘',
  },
  {
    key: '/wallpapers',
    icon: <PictureOutlined />,
    label: '壁纸管理',
  },
  {
    key: '/tarot',
    icon: <StarOutlined />,
    label: '塔罗牌占卜',
  },
  {
    key: '/settings',
    icon: <SettingOutlined />,
    label: '系统设置',
  },
]

interface MainLayoutProps {
  children: ReactNode
}

export default function MainLayout({ children }: MainLayoutProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(false)

  const currentLabel =
    menuItems.find((item) => item.key === location.pathname)?.label ?? '仪表盘'

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        width={220}
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme="light"
        className="app-sider"
      >
        <div className="brand">
          <span className="brand-mark">
            <PictureOutlined />
          </span>
          {!collapsed && (
            <div>
              <div className="brand-name">BingDesk</div>
              <div className="brand-desc">必应壁纸桌面管理</div>
            </div>
          )}
        </div>

        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ borderInlineEnd: 'none' }}
        />

        {!collapsed && (
          <div className="sider-footer">
            <div className="sider-footer-inner">
              <div className="sider-footer-line">版本 v1.0.0</div>
              <div className="sider-footer-line">React + FastAPI</div>
            </div>
          </div>
        )}
      </Sider>

      <Layout>
        <Header className="app-header">
          <span className="app-header-title">{currentLabel}</span>
          <span className="app-status">
            <span className="app-status-dot" />
            运行中
          </span>
        </Header>

        <Content className="app-content">{children}</Content>
      </Layout>
    </Layout>
  )
}
