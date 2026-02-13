import { useState, useEffect } from 'react'

const BACKEND_URL = 'http://localhost:3001'

// Status configurations - functional style
const STATUS_CONFIG = {
  new: { label: 'NEW', shortLabel: 'NEW', color: '#7aa2f7', tag: 'tag-processing' },
  ai_processing: { label: 'AI', shortLabel: 'AI', color: '#7aa2f7', tag: 'tag-processing' },
  resolved: { label: 'RESOLVED', shortLabel: 'OK', color: '#9ece6a', tag: 'tag-resolved' },
  escalated: { label: 'ESCALATED', shortLabel: 'ESC', color: '#f7768e', tag: 'tag-escalated' },
  closed: { label: 'CLOSED', shortLabel: 'DONE', color: '#565f89', tag: 'tag-resolved' }
}

function App() {
  const [tickets, setTickets] = useState([])
  const [selectedTicket, setSelectedTicket] = useState(null)
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // all, escalated, ai_processing

  useEffect(() => {
    fetchTickets()
    const interval = setInterval(fetchTickets, 5000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (selectedTicket) {
      fetchMessages(selectedTicket.id)
      const interval = setInterval(() => fetchMessages(selectedTicket.id), 3000)
      return () => clearInterval(interval)
    }
  }, [selectedTicket])

  const fetchTickets = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/tickets`)
      const data = await response.json()
      setTickets(data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching tickets:', error)
      setLoading(false)
    }
  }

  const fetchMessages = async (ticketId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/tickets/${ticketId}`)
      const data = await response.json()
      setMessages(data.messages || [])
    } catch (error) {
      console.error('Error fetching messages:', error)
    }
  }

  const formatTime = (timestamp) => {
    if (!timestamp) return '--:--'
    const date = new Date(timestamp)
    return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
  }

  const formatDate = (timestamp) => {
    if (!timestamp) return '--.--.----'
    const date = new Date(timestamp)
    return `${String(date.getDate()).padStart(2, '0')}.${String(date.getMonth() + 1).padStart(2, '0')}.${date.getFullYear()}`
  }

  const filteredTickets = tickets.filter(ticket => {
    if (filter === 'escalated') return ticket.status === 'escalated'
    if (filter === 'ai_processing') return ticket.status === 'ai_processing'
    return true
  })

  const getTicketPreview = (ticket) => {
    return ticket.first_message?.substring(0, 60) || 'Без сообщения'
  }

  // Calculate AI metrics for selected ticket
  const calculateMetrics = () => {
    if (!messages.length) return { confidence: 0, iterations: 0, avgResponse: 0, escalations: 0 }

    const aiMessages = messages.filter(m => m.sender_type === 'ai')
    const avgConfidence = aiMessages.reduce((sum, m) => sum + (m.ai_confidence || 0), 0) / (aiMessages.length || 1)
    const escalations = selectedTicket?.status === 'escalated' ? 1 : 0

    return {
      confidence: Math.round(avgConfidence * 100),
      iterations: aiMessages.length,
      avgResponse: '4.2s',
      escalations
    }
  }

  const metrics = selectedTicket ? calculateMetrics() : null

  return (
    <div className="min-h-screen bg-[#1a1b26] text-[#a9b1d6] font-mono text-[13px]">
      {/* Header */}
      <header className="bg-[#16161e] border-b border-[#292e42] px-4 py-1.5 flex items-center justify-between h-9">
        <div className="flex items-center gap-2.5">
          <span className="text-xs font-semibold text-[#7aa2f7]">SULPAK AI HELPDESK</span>
          <span className="text-[#3b4261]">|</span>
          <span className="text-[11px] text-[#565f89]">monitoring</span>
        </div>
        <div className="flex items-center gap-3.5 text-[11px]">
          <div className="flex items-center gap-1.5 text-[#9ece6a]">
            <div className="w-1.5 h-1.5 bg-[#9ece6a] rounded-full"></div>
            ONLINE
          </div>
          <span className="text-[#565f89]">{tickets.length} tickets</span>
          <span className="text-[#3b4261]">{new Date().toLocaleTimeString('ru-RU')}</span>
        </div>
      </header>

      {/* 3-column layout */}
      <div className="grid grid-cols-[280px_1fr_300px] h-[calc(100vh-36px)]">
        {/* Column 1: Ticket List */}
        <div className="bg-[#16161e] border-r border-[#292e42] flex flex-col">
          <div className="px-2.5 py-2 border-b border-[#292e42] flex items-center gap-2">
            <span className="text-[11px] text-[#565f89] uppercase tracking-wider">Тикеты</span>
            <div className="flex gap-0.5 ml-auto">
              <button
                onClick={() => setFilter('all')}
                className={`px-1.5 py-0.5 text-[10px] rounded ${filter === 'all' ? 'text-[#7aa2f7] bg-[#7aa2f7]/10' : 'text-[#565f89]'}`}
              >
                Все
              </button>
              <button
                onClick={() => setFilter('escalated')}
                className={`px-1.5 py-0.5 text-[10px] rounded ${filter === 'escalated' ? 'text-[#7aa2f7] bg-[#7aa2f7]/10' : 'text-[#565f89]'}`}
              >
                ESC
              </button>
              <button
                onClick={() => setFilter('ai_processing')}
                className={`px-1.5 py-0.5 text-[10px] rounded ${filter === 'ai_processing' ? 'text-[#7aa2f7] bg-[#7aa2f7]/10' : 'text-[#565f89]'}`}
              >
                AI
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-[#565f89] text-center">Загрузка...</div>
            ) : filteredTickets.length === 0 ? (
              <div className="p-4 text-[#565f89] text-center">Нет тикетов</div>
            ) : (
              filteredTickets.map(ticket => (
                <div
                  key={ticket.id}
                  onClick={() => setSelectedTicket(ticket)}
                  className={`px-2.5 py-2 border-b border-[#292e42]/50 cursor-pointer transition-colors grid grid-cols-[1fr_auto] gap-1 ${
                    selectedTicket?.id === ticket.id
                      ? 'bg-[#7aa2f7]/8 border-l-2 border-l-[#7aa2f7]'
                      : 'hover:bg-[#7aa2f7]/4'
                  }`}
                >
                  <span className="text-[11px] text-[#7aa2f7]">#{ticket.ticket_number}</span>
                  <span className="text-[10px] text-[#3b4261] text-right">{formatTime(ticket.created_at)}</span>
                  <div className="col-span-2 text-[11px] text-[#565f89] truncate font-sans">
                    {getTicketPreview(ticket)}
                  </div>
                  <div className="col-span-2 flex items-center gap-1.5 mt-0.5">
                    <span className={`text-[9px] px-1.5 py-0.5 rounded font-semibold uppercase tracking-wide ${STATUS_CONFIG[ticket.status]?.tag || 'tag-processing'}`}>
                      {STATUS_CONFIG[ticket.status]?.shortLabel || 'AI'}
                    </span>
                    <span className="text-[10px] text-[#3b4261] ml-auto">{ticket.message_count || 0} msg</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Column 2: Chat */}
        <div className="flex flex-col bg-[#1a1b26]">
          {selectedTicket ? (
            <>
              <div className="px-3.5 py-2 bg-[#16161e] border-b border-[#292e42] flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <h2 className="text-xs font-semibold text-[#c0caf5]">#{selectedTicket.ticket_number}</h2>
                  <span className="text-[11px] text-[#565f89]">@{selectedTicket.telegram_username}</span>
                  <span className={`text-[9px] px-1.5 py-0.5 rounded font-semibold uppercase tracking-wide ${STATUS_CONFIG[selectedTicket.status]?.tag || 'tag-processing'}`}>
                    {STATUS_CONFIG[selectedTicket.status]?.shortLabel || 'AI'}
                  </span>
                </div>
                <div className="flex gap-3.5 text-[10px] text-[#3b4261]">
                  <span>created: {formatTime(selectedTicket.created_at)}</span>
                  {selectedTicket.escalated_at && (
                    <span className="text-[#f7768e]">esc: {formatTime(selectedTicket.escalated_at)}</span>
                  )}
                </div>
              </div>

              <div className="flex-1 overflow-y-auto px-3.5 py-3 flex flex-col gap-2.5">
                {messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`max-w-[75%] px-3 py-2 text-xs leading-relaxed font-sans ${
                      msg.sender_type === 'user'
                        ? 'self-end bg-[#283457] text-[#c0caf5] rounded-lg rounded-br-sm border border-[#3b4a75]'
                        : 'self-start bg-[#1f2335] text-[#a9b1d6] rounded-lg rounded-bl-sm border border-[#292e42]'
                    }`}
                  >
                    <div className={`text-[10px] font-semibold uppercase tracking-wide mb-1 font-mono ${
                      msg.sender_type === 'user' ? 'text-[#7aa2f7]' : 'text-[#bb9af7]'
                    }`}>
                      {msg.sender_type === 'user' ? 'USR' : 'AI'}
                    </div>
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                    {msg.sender_type === 'ai' && msg.ai_confidence > 0 && (
                      <div className="flex items-center gap-2 mt-1.5 pt-1.5 border-t border-[#292e42] font-mono">
                        <span className="text-[10px] text-[#3b4261]">conf:</span>
                        <div className="flex-1 h-[3px] bg-[#292e42] rounded overflow-hidden">
                          <div
                            className="h-full bg-[#9ece6a] rounded"
                            style={{ width: `${msg.ai_confidence * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-[10px] font-semibold text-[#9ece6a]">
                          {Math.round(msg.ai_confidence * 100)}%
                        </span>
                      </div>
                    )}
                    <div className="text-[10px] text-[#3b4261] text-right mt-1 font-mono">
                      {formatTime(msg.created_at)}
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-full text-[#565f89] text-sm">
              Выберите тикет
            </div>
          )}
        </div>

        {/* Column 3: Info Panel */}
        <div className="bg-[#16161e] border-l border-[#292e42] overflow-y-auto p-2.5">
          {selectedTicket ? (
            <>
              {/* Ticket Info */}
              <div className="mb-3.5">
                <div className="text-[10px] text-[#3b4261] uppercase tracking-wider mb-2 pb-1 border-b border-[#292e42]">
                  Тикет
                </div>
                <div className="space-y-0.5">
                  <div className="flex justify-between py-0.5 text-[11px]">
                    <span className="text-[#565f89]">ID</span>
                    <span className="text-[#7aa2f7]">#{selectedTicket.ticket_number}</span>
                  </div>
                  <div className="flex justify-between py-0.5 text-[11px]">
                    <span className="text-[#565f89]">Статус</span>
                    <span style={{ color: STATUS_CONFIG[selectedTicket.status]?.color }}>
                      {STATUS_CONFIG[selectedTicket.status]?.label || 'AI'}
                    </span>
                  </div>
                  <div className="flex justify-between py-0.5 text-[11px]">
                    <span className="text-[#565f89]">Создан</span>
                    <span className="text-[#a9b1d6]">{formatTime(selectedTicket.created_at)}</span>
                  </div>
                  {selectedTicket.escalated_at && (
                    <div className="flex justify-between py-0.5 text-[11px]">
                      <span className="text-[#565f89]">Эскалация</span>
                      <span className="text-[#f7768e]">{formatTime(selectedTicket.escalated_at)}</span>
                    </div>
                  )}
                  <div className="flex justify-between py-0.5 text-[11px]">
                    <span className="text-[#565f89]">Сообщений</span>
                    <span className="text-[#a9b1d6]">{messages.length}</span>
                  </div>
                </div>
              </div>

              {/* Client Info */}
              <div className="mb-3.5">
                <div className="text-[10px] text-[#3b4261] uppercase tracking-wider mb-2 pb-1 border-b border-[#292e42]">
                  Клиент
                </div>
                <div className="space-y-0.5">
                  <div className="flex justify-between py-0.5 text-[11px]">
                    <span className="text-[#565f89]">Username</span>
                    <span className="text-[#a9b1d6]">@{selectedTicket.telegram_username}</span>
                  </div>
                  <div className="flex justify-between py-0.5 text-[11px]">
                    <span className="text-[#565f89]">User ID</span>
                    <span className="text-[#a9b1d6]">{selectedTicket.telegram_user_id}</span>
                  </div>
                </div>
              </div>

              {/* AI Metrics */}
              {metrics && (
                <div className="mb-3.5">
                  <div className="text-[10px] text-[#3b4261] uppercase tracking-wider mb-2 pb-1 border-b border-[#292e42]">
                    AI Метрики
                  </div>
                  <div className="grid grid-cols-2 gap-1.5 mt-1.5">
                    <div className="bg-[#1a1b26] border border-[#292e42] rounded-md p-2 text-center">
                      <div className="text-base font-bold text-[#9ece6a]">{metrics.confidence}%</div>
                      <div className="text-[9px] text-[#3b4261] uppercase tracking-wide mt-0.5">Confidence</div>
                    </div>
                    <div className="bg-[#1a1b26] border border-[#292e42] rounded-md p-2 text-center">
                      <div className="text-base font-bold text-[#e0af68]">{metrics.iterations}</div>
                      <div className="text-[9px] text-[#3b4261] uppercase tracking-wide mt-0.5">Итерации</div>
                    </div>
                    <div className="bg-[#1a1b26] border border-[#292e42] rounded-md p-2 text-center">
                      <div className="text-base font-bold text-[#7aa2f7]">{metrics.avgResponse}</div>
                      <div className="text-[9px] text-[#3b4261] uppercase tracking-wide mt-0.5">Avg Response</div>
                    </div>
                    <div className="bg-[#1a1b26] border border-[#292e42] rounded-md p-2 text-center">
                      <div className="text-base font-bold text-[#f7768e]">{metrics.escalations}</div>
                      <div className="text-[9px] text-[#3b4261] uppercase tracking-wide mt-0.5">Эскалации</div>
                    </div>
                  </div>
                </div>
              )}

              {/* AI Summary */}
              {selectedTicket.ai_summary && (
                <div className="mb-3.5">
                  <div className="text-[10px] text-[#3b4261] uppercase tracking-wider mb-2 pb-1 border-b border-[#292e42]">
                    AI Резюме
                  </div>
                  <div className="bg-[#1a1b26] border border-[#292e42] rounded-md p-2.5 mt-1.5">
                    <p className="text-[11px] text-[#565f89] leading-relaxed font-sans whitespace-pre-wrap">
                      {selectedTicket.ai_summary}
                    </p>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="flex items-center justify-center h-full text-[#565f89] text-xs">
              Выберите тикет
            </div>
          )}
        </div>
      </div>

      {/* Custom CSS for tags */}
      <style>{`
        .tag-escalated {
          background: rgba(247, 118, 142, 0.15);
          color: #f7768e;
        }
        .tag-processing {
          background: rgba(122, 162, 247, 0.12);
          color: #7aa2f7;
        }
        .tag-resolved {
          background: rgba(158, 206, 106, 0.12);
          color: #9ece6a;
        }

        /* Custom scrollbar */
        ::-webkit-scrollbar {
          width: 4px;
        }
        ::-webkit-scrollbar-track {
          background: transparent;
        }
        ::-webkit-scrollbar-thumb {
          background: #292e42;
          border-radius: 2px;
        }
        ::-webkit-scrollbar-thumb:hover {
          background: #3b4261;
        }
      `}</style>
    </div>
  )
}

export default App
