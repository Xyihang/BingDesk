import { useState, useCallback } from 'react'
import {
  Button,
  message,
  Tag,
  Modal,
  Input,
  Slider,
  Drawer,
  List,
  Popconfirm,
  Empty,
  Spin,
  Pagination,
} from 'antd'
import {
  StarOutlined,
  FireOutlined,
  EyeOutlined,
  SyncOutlined,
  CalendarOutlined,
  BookOutlined,
  CompassOutlined,
  HeartOutlined,
  DollarOutlined,
  TeamOutlined,
  BulbOutlined,
  ExperimentOutlined,
  QuestionCircleOutlined,
  HistoryOutlined,
  DeleteOutlined,
  ReloadOutlined,
} from '@ant-design/icons'
import { tarotApi } from '../services/api'
import type { TarotReading, TarotCard, TarotHistoryItem } from '../types'

const spreadPositions = [
  { name: '现状', icon: <EyeOutlined /> },
  { name: '挑战', icon: <FireOutlined /> },
  { name: '过去', icon: <BookOutlined /> },
  { name: '未来', icon: <CompassOutlined /> },
  { name: '目标', icon: <BulbOutlined /> },
  { name: '建议', icon: <HeartOutlined /> },
  { name: '环境', icon: <TeamOutlined /> },
  { name: '希望', icon: <StarOutlined /> },
  { name: '结果', icon: <ExperimentOutlined /> },
  { name: '财富', icon: <DollarOutlined /> },
]

export default function Tarot() {
  const [loading, setLoading] = useState(false)
  const [reading, setReading] = useState<TarotReading | null>(null)
  const [selectedCard, setSelectedCard] = useState<number | null>(null)
  const [spreadType, setSpreadType] = useState<'monthly' | 'daily' | 'celtic'>('monthly')
  const [question, setQuestion] = useState('')
  const [months, setMonths] = useState(1)
  const [historyDrawerOpen, setHistoryDrawerOpen] = useState(false)
  const [historyItems, setHistoryItems] = useState<TarotHistoryItem[]>([])
  const [historyTotal, setHistoryTotal] = useState(0)
  const [historyPage, setHistoryPage] = useState(1)
  const [historyLoading, setHistoryLoading] = useState(false)

  const handleDraw = async () => {
    try {
      setLoading(true)
      setReading(null)
      setSelectedCard(null)

      let response
      if (spreadType === 'monthly') {
        response = await tarotApi.getReading(months, question || undefined)
      } else if (spreadType === 'daily') {
        response = await tarotApi.getDaily()
      } else {
        response = await tarotApi.getCelticCross()
      }

      // 后端返回结构: { success: true, data: {...}, message: "" }
      const readingData = response.data?.data

      // 统一数据结构
      const normalizedReading: TarotReading = {
        spread_type:
          spreadType === 'monthly'
            ? '月度运势'
            : spreadType === 'daily'
              ? '每日塔罗'
              : '凯尔特十字',
        cards: [],
        ai_interpretation: readingData?.ai_interpretation || '',
      }

      if (spreadType === 'monthly' && readingData?.monthly_readings) {
        normalizedReading.cards = readingData.monthly_readings.map((m: any) => ({
          name: m.card?.name || '未知',
          reversed: m.card?.is_reversed || false,
          meaning: m.card?.meaning || '',
          upright_meaning: m.card?.upright_meaning || '',
          reversed_meaning: m.card?.reversed_meaning || '',
        }))
      } else if (spreadType === 'daily' && readingData?.card) {
        normalizedReading.cards = [
          {
            name: readingData.card.name || '未知',
            reversed: readingData.card.is_reversed || false,
            meaning: readingData.card.meaning || '',
            upright_meaning: readingData.card.upright_meaning || '',
            reversed_meaning: readingData.card.reversed_meaning || '',
          },
        ]
      } else if (spreadType === 'celtic' && readingData?.cards) {
        normalizedReading.cards = readingData.cards.map((c: any) => ({
          name: c.card?.name || '未知',
          reversed: c.card?.is_reversed || false,
          meaning: c.card?.meaning || '',
          upright_meaning: c.card?.upright_meaning || '',
          reversed_meaning: c.card?.reversed_meaning || '',
        }))
      }

      setReading(normalizedReading)
      message.success('占卜完成！')
    } catch (error) {
      message.error('占卜失败，请重试')
      console.error('占卜错误:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadHistory = useCallback(async (page = 1) => {
    try {
      setHistoryLoading(true)
      const { data } = await tarotApi.getHistory(page, 20)
      if (data.success) {
        setHistoryItems(data.data.items || [])
        setHistoryTotal(data.data.total || 0)
        setHistoryPage(page)
      }
    } catch {
      message.error('加载历史记录失败')
    } finally {
      setHistoryLoading(false)
    }
  }, [])

  const openHistoryDrawer = () => {
    setHistoryDrawerOpen(true)
    loadHistory(1)
  }

  const handleResumeReading = (item: TarotHistoryItem) => {
    const typeMap: Record<string, 'monthly' | 'daily' | 'celtic'> = {
      monthly: 'monthly',
      daily: 'daily',
      celtic: 'celtic',
    }
    setSpreadType(typeMap[item.reading_type] || 'monthly')
    if (item.question) setQuestion(item.question)
    if (item.period_months) setMonths(item.period_months)

    const normalizedReading: TarotReading = {
      spread_type: item.reading_type,
      cards: (item.cards || []).map((c: any) => ({
        name: c.name || '未知',
        reversed: c.is_reversed ?? c.reversed ?? false,
        meaning: c.meaning || '',
        upright_meaning: c.upright_meaning || '',
        reversed_meaning: c.reversed_meaning || '',
      })),
      ai_interpretation: item.ai_interpretation,
    }
    setReading(normalizedReading)
    setSelectedCard(null)
    setHistoryDrawerOpen(false)
    message.success('已恢复历史占卜结果')
  }

  const handleDeleteHistory = async (id: number) => {
    try {
      await tarotApi.deleteHistory(id)
      message.success('已删除')
      loadHistory(historyPage)
    } catch {
      message.error('删除失败')
    }
  }

  const getSpreadTitle = () => {
    switch (spreadType) {
      case 'monthly':
        return '月度运势占卜'
      case 'daily':
        return '每日塔罗'
      case 'celtic':
        return '凯尔特十字'
      default:
        return '塔罗占卜'
    }
  }

  const getSpreadDescription = () => {
    switch (spreadType) {
      case 'monthly':
        return '预测未来 1-12 个月的运势走向'
      case 'daily':
        return '解读今日的运势和建议'
      case 'celtic':
        return '深入分析当前状况的十字牌阵'
      default:
        return ''
    }
  }

  const spreadTypes = [
    { key: 'monthly' as const, label: '月度运势', icon: <CalendarOutlined />, desc: '1-12个月' },
    { key: 'daily' as const, label: '每日塔罗', icon: <StarOutlined />, desc: '今日运势' },
    { key: 'celtic' as const, label: '凯尔特十字', icon: <CompassOutlined />, desc: '深度分析' },
  ]

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">塔罗牌占卜</h1>
          <p className="page-subtitle">探索未知，解读命运的指引</p>
        </div>
        <Button icon={<HistoryOutlined />} onClick={openHistoryDrawer} size="large">
          历史记录
        </Button>
      </div>

      <div className="spread-options">
        {spreadTypes.map((type) => (
          <div
            key={type.key}
            className={`spread-option ${spreadType === type.key ? 'is-active' : ''}`}
            onClick={() => {
              setSpreadType(type.key)
              setReading(null)
            }}
          >
            <span className="spread-icon">{type.icon}</span>
            <div className="spread-name">{type.label}</div>
            <div className="spread-desc">{type.desc}</div>
          </div>
        ))}
      </div>

      <section className="panel">
        <div className="panel-header" style={{ justifyContent: 'center' }}>
          <div>
            <div className="tarot-type-title">{getSpreadTitle()}</div>
            <div className="tarot-type-desc">{getSpreadDescription()}</div>
          </div>
        </div>

        {spreadType === 'monthly' && (
          <div className="stack">
            <div className="slider-block">
              <div className="setting-name" style={{ marginBottom: 'var(--space-2)' }}>
                <CalendarOutlined /> 预测时长：{months} 个月
              </div>
              <Slider
                min={1}
                max={12}
                step={1}
                value={months}
                onChange={setMonths}
                marks={{
                  1: '1月',
                  3: '3月',
                  6: '6月',
                  9: '9月',
                  12: '12月',
                }}
                tooltip={{ formatter: (v) => `${v}个月` }}
              />
            </div>

            <div className="question-row">
              <div className="question-label">
                <QuestionCircleOutlined />
                您想询问什么问题？（可选）
              </div>
              <Input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="例如：我未来的事业发展如何？"
                maxLength={100}
                showCount
              />
            </div>
          </div>
        )}

        <div className="center-action">
          <Button
            type="primary"
            icon={<SyncOutlined spin={loading} />}
            size="large"
            onClick={handleDraw}
            loading={loading}
          >
            {loading ? '正在抽牌...' : '开始占卜'}
          </Button>
        </div>
      </section>

      {reading && reading.cards && (
        <section className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <StarOutlined />
              <span>占卜结果</span>
              <Tag color="blue">{reading.spread_type || '未知牌阵'}</Tag>
            </div>
          </div>

          <div className="tarot-grid">
            {reading.cards?.map((card: TarotCard, index: number) => (
              <div
                key={index}
                className="tarot-card-face"
                onClick={() => setSelectedCard(index)}
              >
                <span className="tarot-card-icon">{spreadPositions[index]?.icon || <StarOutlined />}</span>
                <span className="tarot-card-name">{card.name}</span>
                <span className="tarot-card-pos">
                  {spreadPositions[index]?.name || `位置 ${index + 1}`}
                </span>
                {card.reversed && <span className="tarot-reversed">逆位</span>}
              </div>
            ))}
          </div>

          {reading.ai_interpretation && (
            <div className="interpretation">
              <div className="interpretation-title">
                <BulbOutlined />
                <span>AI 深度解读</span>
              </div>
              <div className="interpretation-body">
                {reading.ai_interpretation || '暂无解读'}
              </div>
            </div>
          )}
        </section>
      )}

      <Modal
        open={selectedCard !== null}
        onCancel={() => setSelectedCard(null)}
        footer={null}
        title={
          <div className="panel-title">
            <StarOutlined />
            <span>牌意详解</span>
          </div>
        }
      >
        {selectedCard !== null && reading && reading.cards && reading.cards[selectedCard] && (
          <div className="stack">
            <div
              className="detail-image"
              style={{ height: 240, alignItems: 'center' }}
            >
              <StarOutlined
                style={{ fontSize: 'var(--text-2xl)', color: 'var(--color-neutral-400)' }}
              />
            </div>

            <div style={{ textAlign: 'center' }}>
              <span className="page-title">{reading.cards[selectedCard].name}</span>
              {reading.cards[selectedCard].reversed && (
                <Tag color="error" style={{ marginLeft: 'var(--space-2)' }}>
                  逆位
                </Tag>
              )}
            </div>

            <div className="detail-item">
              <div className="detail-label">位置</div>
              <div className="detail-value">
                {spreadPositions[selectedCard]?.name || `位置 ${selectedCard + 1}`}
              </div>
            </div>

            <div className="detail-item">
              <div className="detail-label">正位含义</div>
              <div className="detail-value" style={{ fontWeight: 400 }}>
                {reading.cards[selectedCard].upright_meaning ||
                  reading.cards[selectedCard].meaning ||
                  '积极的能量和顺利的发展'}
              </div>
            </div>

            <div className="detail-item">
              <div className="detail-label">逆位含义</div>
              <div className="detail-value" style={{ fontWeight: 400 }}>
                {reading.cards[selectedCard].reversed_meaning ||
                  '阻碍、挑战或需要反思的方面'}
              </div>
            </div>
          </div>
        )}
      </Modal>

      <Drawer
        title={
          <div className="panel-title">
            <HistoryOutlined />
            <span>占卜历史记录</span>
            <Tag color="blue">{historyTotal}</Tag>
          </div>
        }
        open={historyDrawerOpen}
        onClose={() => setHistoryDrawerOpen(false)}
        width={420}
      >
        <Spin spinning={historyLoading}>
          {historyItems.length === 0 && !historyLoading ? (
            <Empty description="暂无历史记录" />
          ) : (
            <>
              <List
                dataSource={historyItems}
                split={false}
                renderItem={(item) => (
                  <div className="history-item" onClick={() => handleResumeReading(item)}>
                    <div className="history-head">
                      <div className="history-tags">
                        <Tag
                          color={
                            item.reading_type === 'monthly'
                              ? 'blue'
                              : item.reading_type === 'daily'
                                ? 'green'
                                : 'purple'
                          }
                        >
                          {item.reading_type === 'monthly'
                            ? '月度运势'
                            : item.reading_type === 'daily'
                              ? '每日塔罗'
                              : '凯尔特十字'}
                        </Tag>
                        {item.overall_fortune && (
                          <Tag color={item.overall_fortune === '吉' ? 'success' : 'warning'}>
                            {item.overall_fortune}
                          </Tag>
                        )}
                      </div>

                      <div className="history-actions">
                        <Button
                          type="text"
                          size="small"
                          icon={<ReloadOutlined />}
                          onClick={(e) => {
                            e.stopPropagation()
                            handleResumeReading(item)
                          }}
                          title="续查"
                        />
                        <Popconfirm
                          title="确定删除这条记录？"
                          onConfirm={(e) => {
                            e?.stopPropagation()
                            handleDeleteHistory(item.id)
                          }}
                          onCancel={(e) => e?.stopPropagation()}
                        >
                          <Button
                            type="text"
                            size="small"
                            danger
                            icon={<DeleteOutlined />}
                            onClick={(e) => e.stopPropagation()}
                            title="删除"
                          />
                        </Popconfirm>
                      </div>
                    </div>

                    {item.question && <div className="history-question">问：{item.question}</div>}
                    <div className="history-date">{item.created_at}</div>

                    <div className="history-cards">
                      {(item.cards || []).slice(0, 4).map((c: any, i: number) => (
                        <Tag key={i} color={c.is_reversed ? 'orange' : 'cyan'}>
                          {c.is_reversed ? '逆' : '正'} {c.name}
                        </Tag>
                      ))}
                      {item.cards && item.cards.length > 4 && (
                        <Tag>+{item.cards.length - 4}</Tag>
                      )}
                    </div>
                  </div>
                )}
              />

              {historyTotal > 20 && (
                <div className="center-action">
                  <Pagination
                    size="small"
                    current={historyPage}
                    total={historyTotal}
                    pageSize={20}
                    onChange={(p) => loadHistory(p)}
                    showSizeChanger={false}
                  />
                </div>
              )}
            </>
          )}
        </Spin>
      </Drawer>
    </div>
  )
}
