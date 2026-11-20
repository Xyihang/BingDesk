import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { App as AntdApp, Spin } from 'antd'
import MainLayout from './components/Layout/MainLayout'

const Dashboard = lazy(() => import('./pages/Dashboard'))
const Wallpapers = lazy(() => import('./pages/Wallpapers'))
const Settings = lazy(() => import('./pages/Settings'))
const Tarot = lazy(() => import('./pages/Tarot'))

const PageLoading = () => (
  <div className="page-loading">
    <Spin size="large" />
  </div>
)

function App() {
  return (
    <AntdApp>
      <BrowserRouter>
        <MainLayout>
          <Suspense fallback={<PageLoading />}>
            <Routes>
              <Route path="/" element={<Navigate to="/wallpapers" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/wallpapers" element={<Wallpapers />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/tarot" element={<Tarot />} />
            </Routes>
          </Suspense>
        </MainLayout>
      </BrowserRouter>
    </AntdApp>
  )
}

export default App
