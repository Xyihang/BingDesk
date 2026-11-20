import { useState, useEffect } from 'react'
import { Form, Switch, Select, Button, Spin, Slider, Tabs, Input, Space, Tooltip, Tag } from 'antd'
import {
  ClockCircleOutlined,
  SyncOutlined,
  SaveOutlined,
  ReloadOutlined,
  InfoCircleOutlined,
  RocketOutlined,
  PictureOutlined,
  CopyOutlined,
  CodeOutlined,
  FileTextOutlined,
  CheckOutlined,
  EyeInvisibleOutlined,
  LockOutlined,
  KeyOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
} from '@ant-design/icons'
import { useAppStore } from '../stores/appStore'
import { settingsApi, systemApi, authApi } from '../services/api'
import { App } from 'antd'

export default function Settings() {
  const { fetchSystemStatus, systemStatus } = useAppStore()
  const { message, modal } = App.useApp()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [form] = Form.useForm()
  const [settings, setSettings] = useState<Record<string, string>>({})
  const [scriptsLoading, setScriptsLoading] = useState(false)
  const [scriptBat, setScriptBat] = useState('')
  const [scriptPs, setScriptPs] = useState('')
  const [scriptBatHidden, setScriptBatHidden] = useState('')
  const [scriptPsHidden, setScriptPsHidden] = useState('')
  const [scriptsLoaded, setScriptsLoaded] = useState(false)
  const [copiedBat, setCopiedBat] = useState(false)
  const [copiedPs, setCopiedPs] = useState(false)
  const [copiedBatHidden, setCopiedBatHidden] = useState(false)
  const [copiedPsHidden, setCopiedPsHidden] = useState(false)

  const [appPasswordForm, setAppPasswordForm] = useState({ current: '', newPwd: '', confirm: '' })
  const [gridPasswordForm, setGridPasswordForm] = useState({ current: '', newPwd: '', confirm: '' })
  const [changingAppPassword, setChangingAppPassword] = useState(false)
  const [changingGridPassword, setChangingGridPassword] = useState(false)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    setLoading(true)
    try {
      const response = await settingsApi.getAll()
      const settingsMap: Record<string, string> = {}
      const items = response.data.items || []
      items.forEach((setting: { key: string; value: string }) => {
        settingsMap[setting.key] = setting.value
      })
      setSettings(settingsMap)
      form.setFieldsValue(settingsMap)
    } catch (error) {
      message.error('加载设置失败')
    }
    setLoading(false)
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      const values = await form.validateFields()

      for (const [key, value] of Object.entries(values)) {
        await settingsApi.update(key, String(value))
      }

      message.success('设置保存成功')
      await loadSettings()
      await fetchSystemStatus()
    } catch (error) {
      message.error('保存设置失败')
    } finally {
      setSaving(false)
    }
  }

  const handleToggleAutoStart = async () => {
    try {
      await systemApi.setAutostart(!systemStatus?.auto_start)
      message.success(`开机自启已${systemStatus?.auto_start ? '禁用' : '启用'}`)
      await fetchSystemStatus()
    } catch (error) {
      message.error('操作失败')
    }
  }

  const handleRestartScheduler = async () => {
    try {
      await systemApi.stopScheduler()
      await systemApi.startScheduler(parseInt(settings.change_interval || '60'))
      message.success('定时任务已重启')
      await fetchSystemStatus()
    } catch (error) {
      message.error('重启失败')
    }
  }

  const handleToggleScheduler = async () => {
    try {
      if (systemStatus?.is_running) {
        await systemApi.stopScheduler()
        message.success('自动切换已停止')
      } else {
        await systemApi.startScheduler(parseInt(settings.change_interval || '60'))
        message.success('自动切换已启动')
      }
      await fetchSystemStatus()
    } catch (error) {
      message.error('操作失败')
    }
  }

  const handleStopServices = () => {
    modal.confirm({
      title: '确认停止服务',
      content: '此操作将停止前后端所有服务，确定要继续吗？',
      okText: '确定',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: async () => {
        modal.confirm({
          title: '再次确认',
          content: '服务停止后需要手动重启，是否继续？',
          okText: '停止',
          cancelText: '取消',
          okButtonProps: { danger: true },
          onOk: async () => {
            try {
              const { data } = await systemApi.stopServices()
              if (data.success) {
                if (data.processes.length > 0) {
                  message.success(data.message)
                } else {
                  message.info(data.message)
                }
              }
            } catch (error) {
              message.error('停止服务失败')
            }
          },
        })
      },
    })
  }

  const handleLoadScripts = async () => {
    if (scriptsLoaded) return
    setScriptsLoading(true)
    try {
      const res = await systemApi.getAutostartScripts()
      setScriptBat(res.data.bat)
      setScriptPs(res.data.powershell)
      setScriptBatHidden(res.data.bat_hidden)
      setScriptPsHidden(res.data.powershell_hidden)
      setScriptsLoaded(true)
    } catch (error) {
      message.error('获取脚本内容失败')
    } finally {
      setScriptsLoading(false)
    }
  }

  const handleCopy = async (text: string, type: 'bat' | 'ps' | 'batHidden' | 'psHidden') => {
    try {
      await navigator.clipboard.writeText(text)
      message.success(`${type.startsWith('bat') ? 'BAT' : 'PowerShell'} 脚本已复制到剪贴板`)
      if (type === 'bat') {
        setCopiedBat(true)
        setTimeout(() => setCopiedBat(false), 2000)
      } else if (type === 'ps') {
        setCopiedPs(true)
        setTimeout(() => setCopiedPs(false), 2000)
      } else if (type === 'batHidden') {
        setCopiedBatHidden(true)
        setTimeout(() => setCopiedBatHidden(false), 2000)
      } else {
        setCopiedPsHidden(true)
        setTimeout(() => setCopiedPsHidden(false), 2000)
      }
    } catch {
      message.error('复制失败，请手动复制')
    }
  }

  const handleChangePassword = async (type: 'app' | 'grid') => {
    const form = type === 'app' ? appPasswordForm : gridPasswordForm
    const setForm = type === 'app' ? setAppPasswordForm : setGridPasswordForm
    const setLoading = type === 'app' ? setChangingAppPassword : setChangingGridPassword
    const label = type === 'app' ? '操作密码' : '网格密码'

    if (!form.current || !form.newPwd || !form.confirm) {
      message.error('请填写所有字段')
      return
    }
    if (form.newPwd !== form.confirm) {
      message.error('两次输入的新密码不一致')
      return
    }
    if (form.newPwd.length < 4) {
      message.error('新密码长度不能少于4位')
      return
    }
    if (form.current === form.newPwd) {
      message.error('新密码不能与当前密码相同')
      return
    }

    setLoading(true)
    try {
      const { data } = await authApi.changePassword(form.current, form.newPwd, type)
      if (data.success) {
        message.success(`${label}修改成功`)
        setForm({ current: '', newPwd: '', confirm: '' })
      } else {
        message.error(data.message || '修改失败')
      }
    } catch {
      message.error('修改失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  const renderScriptTab = (
    description: string,
    text: string,
    copied: boolean,
    type: 'bat' | 'ps' | 'batHidden' | 'psHidden',
  ) => (
    <div>
      <div className="code-toolbar">
        <span className="code-hint">{description}</span>
        <Button
          type={copied ? 'default' : 'primary'}
          icon={copied ? <CheckOutlined /> : <CopyOutlined />}
          size="small"
          onClick={() => handleCopy(text, type)}
        >
          {copied ? '已复制' : '复制'}
        </Button>
      </div>
      <pre className="code-block">
        <code>{text}</code>
      </pre>
    </div>
  )

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
          <h1 className="page-title">系统设置</h1>
          <p className="page-subtitle">配置壁纸下载、自动切换等系统参数</p>
        </div>
        <Button
          type="primary"
          icon={<SaveOutlined />}
          size="large"
          onClick={handleSave}
          loading={saving}
        >
          保存设置
        </Button>
      </div>

      <Form form={form} layout="vertical">
        <div className="settings-grid">
          <section className="panel">
            <div className="panel-header">
              <div className="panel-title">
                <PictureOutlined />
                <span>壁纸设置</span>
              </div>
            </div>

            <Form.Item
              name="download_quality"
              label={
                <span>
                  下载质量{' '}
                  <Tooltip title="选择壁纸下载的分辨率质量">
                    <InfoCircleOutlined style={{ color: 'var(--color-neutral-400)' }} />
                  </Tooltip>
                </span>
              }
            >
              <Select size="large">
                <Select.Option value="uhd">超高清 (UHD)</Select.Option>
                <Select.Option value="fhd">全高清 (FHD)</Select.Option>
                <Select.Option value="hd">高清 (HD)</Select.Option>
              </Select>
            </Form.Item>

            <Form.Item name="change_interval" label="自动切换间隔（分钟）">
              <Slider
                min={1}
                max={1440}
                step={1}
                marks={{
                  1: '1分钟',
                  60: '1小时',
                  360: '6小时',
                  720: '12小时',
                  1440: '24小时',
                }}
                tooltip={{ formatter: (value) => `${value} 分钟` }}
              />
            </Form.Item>

            <Form.Item name="auto_start" valuePropName="checked" style={{ marginBottom: 0 }}>
              <div className="setting-row">
                <div className="setting-main">
                  <span className="info-icon">
                    <RocketOutlined />
                  </span>
                  <div>
                    <div className="setting-name">开机自启</div>
                    <div className="setting-desc">系统启动时自动运行壁纸管理</div>
                  </div>
                </div>
                <Switch
                  checked={Boolean(systemStatus?.auto_start)}
                  onChange={handleToggleAutoStart}
                />
              </div>
            </Form.Item>
          </section>

          <section className="panel">
            <div className="panel-header">
              <div className="panel-title">
                <SyncOutlined />
                <span>定时任务</span>
              </div>
              <Tag color={systemStatus?.is_running ? 'success' : 'default'}>
                {systemStatus?.is_running ? '运行中' : '已停止'}
              </Tag>
            </div>

            <div className="stack">
              <div className="setting-row">
                <div className="setting-main">
                  <span className="info-icon">
                    <ClockCircleOutlined />
                  </span>
                  <div>
                    <div className="setting-name">自动切换状态</div>
                    <div className="setting-desc">定时更换桌面壁纸</div>
                  </div>
                </div>
                <span
                  className="setting-value"
                  style={{
                    color: systemStatus?.is_running
                      ? 'var(--color-success)'
                      : 'var(--color-neutral-500)',
                  }}
                >
                  {systemStatus?.is_running ? '运行中' : '已停止'}
                </span>
              </div>

              <div className="setting-row">
                <div className="setting-main">
                  <span className="info-icon">
                    <ClockCircleOutlined />
                  </span>
                  <div>
                    <div className="setting-name">下次切换时间</div>
                    <div className="setting-desc">自动更换壁纸的预计时间</div>
                  </div>
                </div>
                <span className="setting-value">
                  {systemStatus?.next_change_time
                    ? new Date(systemStatus.next_change_time).toLocaleTimeString()
                    : '未设置'}
                </span>
              </div>

              <Button
                type={systemStatus?.is_running ? 'default' : 'primary'}
                danger={Boolean(systemStatus?.is_running)}
                icon={
                  systemStatus?.is_running ? <PauseCircleOutlined /> : <PlayCircleOutlined />
                }
                block
                size="large"
                onClick={handleToggleScheduler}
              >
                {systemStatus?.is_running ? '停止自动切换' : '启动自动切换'}
              </Button>

              <Button
                type="primary"
                icon={<ReloadOutlined />}
                block
                size="large"
                onClick={handleRestartScheduler}
              >
                重启定时任务
              </Button>

              <Button
                danger
                icon={<PauseCircleOutlined />}
                block
                size="large"
                onClick={handleStopServices}
              >
                一键停止前后端
              </Button>
            </div>
          </section>
        </div>
      </Form>

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">
            <KeyOutlined />
            <span>密码管理</span>
          </div>
        </div>

        <div className="settings-grid">
          <div>
            <div className="setting-name">
              <LockOutlined /> 操作密码
            </div>
            <div className="setting-desc" style={{ marginBottom: 'var(--space-4)' }}>
              保留用于访问验证扩展，可随时修改
            </div>
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Input.Password
                placeholder="当前密码"
                value={appPasswordForm.current}
                onChange={(e) =>
                  setAppPasswordForm({ ...appPasswordForm, current: e.target.value })
                }
                prefix={<LockOutlined />}
              />
              <Input.Password
                placeholder="新密码（至少4位）"
                value={appPasswordForm.newPwd}
                onChange={(e) =>
                  setAppPasswordForm({ ...appPasswordForm, newPwd: e.target.value })
                }
                prefix={<KeyOutlined />}
              />
              <Input.Password
                placeholder="确认新密码"
                value={appPasswordForm.confirm}
                onChange={(e) =>
                  setAppPasswordForm({ ...appPasswordForm, confirm: e.target.value })
                }
                prefix={<KeyOutlined />}
                onPressEnter={() => handleChangePassword('app')}
              />
              <Button
                type="primary"
                block
                loading={changingAppPassword}
                onClick={() => handleChangePassword('app')}
              >
                修改操作密码
              </Button>
            </Space>
          </div>

          <div>
            <div className="setting-name">
              <LockOutlined /> 网格密码
            </div>
            <div className="setting-desc" style={{ marginBottom: 'var(--space-4)' }}>
              保留用于网格验证扩展，可随时修改
            </div>
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Input.Password
                placeholder="当前密码"
                value={gridPasswordForm.current}
                onChange={(e) =>
                  setGridPasswordForm({ ...gridPasswordForm, current: e.target.value })
                }
                prefix={<LockOutlined />}
              />
              <Input.Password
                placeholder="新密码（至少4位）"
                value={gridPasswordForm.newPwd}
                onChange={(e) =>
                  setGridPasswordForm({ ...gridPasswordForm, newPwd: e.target.value })
                }
                prefix={<KeyOutlined />}
              />
              <Input.Password
                placeholder="确认新密码"
                value={gridPasswordForm.confirm}
                onChange={(e) =>
                  setGridPasswordForm({ ...gridPasswordForm, confirm: e.target.value })
                }
                prefix={<KeyOutlined />}
                onPressEnter={() => handleChangePassword('grid')}
              />
              <Button
                type="primary"
                block
                loading={changingGridPassword}
                onClick={() => handleChangePassword('grid')}
              >
                修改网格密码
              </Button>
            </Space>
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div className="panel-title">
            <CodeOutlined />
            <span>一键启动脚本</span>
          </div>
        </div>

        {!scriptsLoaded ? (
          <div className="empty-state" style={{ border: 'none', padding: 'var(--space-8)' }}>
            <span className="empty-text">生成可复制的一键启动命令，方便在其他设备上使用</span>
            <Button
              type="primary"
              icon={<CodeOutlined />}
              size="large"
              loading={scriptsLoading}
              onClick={handleLoadScripts}
            >
              生成启动脚本
            </Button>
          </div>
        ) : (
          <Tabs
            defaultActiveKey="bat"
            items={[
              {
                key: 'bat',
                label: (
                  <span>
                    <FileTextOutlined /> BAT 脚本
                  </span>
                ),
                children: renderScriptTab(
                  '将以下内容保存为 .bat 文件，双击即可启动前后端（带命令行窗口）',
                  scriptBat,
                  copiedBat,
                  'bat',
                ),
              },
              {
                key: 'ps',
                label: (
                  <span>
                    <CodeOutlined /> PowerShell 脚本
                  </span>
                ),
                children: renderScriptTab(
                  '将以下内容保存为 .ps1 文件，在 PowerShell 中运行（带命令行窗口）',
                  scriptPs,
                  copiedPs,
                  'ps',
                ),
              },
              {
                key: 'bat_hidden',
                label: (
                  <span>
                    <EyeInvisibleOutlined /> BAT 静默
                  </span>
                ),
                children: renderScriptTab(
                  '保存为 .bat 文件，双击后无窗口静默启动，适合开机自启',
                  scriptBatHidden,
                  copiedBatHidden,
                  'batHidden',
                ),
              },
              {
                key: 'ps_hidden',
                label: (
                  <span>
                    <EyeInvisibleOutlined /> PowerShell 静默
                  </span>
                ),
                children: renderScriptTab(
                  '保存为 .ps1 文件，运行后无窗口静默启动，适合开机自启',
                  scriptPsHidden,
                  copiedPsHidden,
                  'psHidden',
                ),
              },
            ]}
          />
        )}
      </section>
    </div>
  )
}
