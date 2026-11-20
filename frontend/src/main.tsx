import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import App from './App'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#2563eb',
          colorText: '#111827',
          colorTextSecondary: '#6b7280',
          colorTextTertiary: '#9ca3af',
          colorBorder: '#d1d5db',
          colorBorderSecondary: '#e5e7eb',
          colorBgLayout: '#f8f9fa',
          colorSuccess: '#16a34a',
          colorWarning: '#d97706',
          colorError: '#dc2626',
          borderRadius: 8,
          fontSize: 14,
          controlHeight: 32,
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.08)',
          boxShadowSecondary: '0 4px 12px rgba(0, 0, 0, 0.1)',
        },
        components: {
          Button: {
            primaryShadow: 'none',
            defaultShadow: 'none',
          },
          Card: {
            paddingLG: 24,
          },
          Layout: {
            headerBg: '#ffffff',
            siderBg: '#ffffff',
            bodyBg: '#f8f9fa',
          },
          Menu: {
            itemSelectedBg: '#eff6ff',
            itemSelectedColor: '#2563eb',
          },
        },
      }}
    >
      <App />
    </ConfigProvider>
  </React.StrictMode>,
)
