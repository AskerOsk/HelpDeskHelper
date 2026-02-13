import { useState, useEffect } from 'react'

const BACKEND_URL = 'http://localhost:3001'

// Status configurations with neon colors
const STATUS_CONFIG = {
  new: {
    label: 'Новый',
    color: 'text-blue-400',
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    icon: '🆕'
  },
  ai_processing: {
    label: 'AI Обработка',
    color: 'text-neon-green',
    bg: 'bg-neon-green/10',
    border: 'border-neon-green/30',
    icon: '🤖',
    glow: true
  },
  resolved: {
    label: 'Решён',
    color: 'text-green-400',
    bg: 'bg-green-500/10',
    border: 'border-green-500/30',
    icon: '✅'
  },
  escalated: {
    label: 'Эскалирован',
    color: 'text-neon-orange',
    bg: 'bg-neon-orange/10',
    border: 'border-neon-orange/30',
    icon: '🚨',
    glow: true
  },
  closed: {
    label: 'Закрыт',
    color: 'text-gray-500',
    bg: 'bg-gray-500/10',
    border: 'border-gray-500/30',
    icon: '🔒'
  }
}

function App() {
  const [tickets, setTickets] = useState([])
  const [selectedTicket, setSelectedTicket] = useState(null)
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)

  // Fetch tickets every 5 seconds
  useEffect(() => {
    fetchTickets()
    const interval = setInterval(fetchTickets, 5000)
    return () => clearInterval(interval)
  }, [])

  // Fetch messages when ticket selected
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
    const date = new Date(timestamp)
    const now = new Date()
    const isToday = date.toDateString() === now.toDateString()

    if (isToday) {
      return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
    }
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const StatusBadge = ({ status }) => {
    const config = STATUS_CONFIG[status] || STATUS_CONFIG.new
    return (
      <div className={`
        inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium
        ${config.bg} ${config.color} ${config.border} border
        ${config.glow ? 'animate-pulse-slow shadow-neon-green' : ''}
      `}>
        <span className="text-sm">{config.icon}</span>
        {config.label}
      </div>
    )
  }

  const TicketCard = ({ ticket }) => {
    const isSelected = selectedTicket?.id === ticket.id

    return (
      <button
        onClick={() => setSelectedTicket(ticket)}
        className={`
          w-full text-left p-4 rounded-xl transition-all duration-200
          border backdrop-blur-sm
          ${isSelected
            ? 'bg-dark-card border-neon-green shadow-neon-green'
            : 'bg-dark-panel/50 border-dark-border hover:border-neon-green/50 hover:bg-dark-card/80'
          }
        `}
      >
        <div className="flex items-start justify-between mb-2">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-neon-green font-mono text-sm">
                #{ticket.ticket_number}
              </span>
              <span className="text-gray-500 text-xs">
                @{ticket.telegram_username}
              </span>
            </div>
            <StatusBadge status={ticket.status} />
          </div>
        </div>

        <p className="text-gray-400 text-sm line-clamp-2 mt-3 mb-2">
          {ticket.first_message || 'Нет сообщений'}
        </p>

        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-500">
            {formatTime(ticket.created_at)}
          </span>
          <span className="text-neon-green/70 flex items-center gap-1">
            💬 {ticket.message_count || 0}
          </span>
        </div>
      </button>
    )
  }

  const MessageBubble = ({ message }) => {
    const isAI = message.sender_type === 'ai'

    return (
      <div className={`flex ${isAI ? 'justify-start' : 'justify-end'} mb-4`}>
        <div className={`
          max-w-[70%] rounded-2xl p-4 backdrop-blur-sm
          ${isAI
            ? 'bg-dark-card border border-neon-green/20'
            : 'bg-gradient-to-br from-neon-orange/20 to-neon-orange/10 border border-neon-orange/20'
          }
        `}>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-medium">
              {isAI ? '🤖 AI Ассистент' : '👤 Пользователь'}
            </span>
            <span className="text-xs text-gray-500">
              {formatTime(message.created_at)}
            </span>
          </div>

          {message.media_type && (
            <div className="mb-3">
              {message.media_type === 'photo' ? (
                <a
                  href={message.media_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block rounded-lg overflow-hidden border border-dark-border hover:border-neon-green/50 transition-colors"
                >
                  <img
                    src={message.media_url}
                    alt="Attached"
                    className="max-w-full h-auto"
                  />
                </a>
              ) : message.media_type === 'video' ? (
                <video
                  src={message.media_url}
                  controls
                  className="max-w-full rounded-lg border border-dark-border"
                />
              ) : null}
            </div>
          )}

          <p className={`text-sm whitespace-pre-wrap ${isAI ? 'text-gray-200' : 'text-gray-300'}`}>
            {message.content}
          </p>

          {message.ai_confidence !== null && message.ai_confidence !== undefined && (
            <div className="mt-2 pt-2 border-t border-dark-border">
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <span>Уверенность AI:</span>
                <div className="flex-1 bg-dark-bg rounded-full h-1.5 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-neon-green to-green-400 transition-all"
                    style={{ width: `${(message.ai_confidence * 100)}%` }}
                  />
                </div>
                <span className="text-neon-green font-medium">
                  {(message.ai_confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-dark-bg text-gray-100">
      {/* Header */}
      <header className="border-b border-dark-border bg-dark-panel/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-[1920px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-neon-green to-green-400 flex items-center justify-center shadow-glow-green">
                  <span className="text-2xl">🤖</span>
                </div>
                <div>
                  <h1 className="text-xl font-bold bg-gradient-to-r from-neon-green via-green-400 to-neon-green bg-clip-text text-transparent">
                    Sulpak AI HelpDesk
                  </h1>
                  <p className="text-xs text-gray-500">Мониторинг AI-ассистента</p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-dark-card border border-dark-border">
                <div className="w-2 h-2 rounded-full bg-neon-green animate-pulse shadow-glow-green" />
                <span className="text-sm text-gray-400">AI Online</span>
              </div>
              <div className="text-sm text-gray-500">
                {tickets.length} тикетов
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-[1920px] mx-auto flex h-[calc(100vh-73px)]">
        {/* Left Panel - Ticket List */}
        <div className="w-[400px] border-r border-dark-border bg-dark-panel/30 backdrop-blur-sm overflow-hidden flex flex-col">
          <div className="p-4 border-b border-dark-border">
            <h2 className="text-lg font-semibold text-neon-green flex items-center gap-2">
              <span>📋</span>
              Тикеты
            </h2>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {loading ? (
              <div className="text-center py-12">
                <div className="inline-block w-8 h-8 border-4 border-neon-green/20 border-t-neon-green rounded-full animate-spin" />
                <p className="text-gray-500 mt-4">Загрузка...</p>
              </div>
            ) : tickets.length === 0 ? (
              <div className="text-center py-12">
                <span className="text-6xl opacity-20">📭</span>
                <p className="text-gray-500 mt-4">Нет тикетов</p>
              </div>
            ) : (
              tickets.map(ticket => (
                <TicketCard key={ticket.id} ticket={ticket} />
              ))
            )}
          </div>
        </div>

        {/* Right Panel - Chat Thread */}
        <div className="flex-1 flex flex-col bg-dark-bg">
          {selectedTicket ? (
            <>
              {/* Chat Header */}
              <div className="p-6 border-b border-dark-border bg-dark-panel/30 backdrop-blur-sm">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-neon-green font-mono">
                        #{selectedTicket.ticket_number}
                      </h3>
                      <span className="text-gray-400">@{selectedTicket.telegram_username}</span>
                    </div>
                    <StatusBadge status={selectedTicket.status} />
                  </div>
                  <div className="text-right text-sm text-gray-500">
                    <div>Создан: {formatTime(selectedTicket.created_at)}</div>
                    {selectedTicket.escalated_at && (
                      <div className="text-neon-orange">
                        Эскалирован: {formatTime(selectedTicket.escalated_at)}
                      </div>
                    )}
                  </div>
                </div>

                {selectedTicket.ai_summary && (
                  <div className="mt-4 p-4 rounded-lg bg-neon-orange/5 border border-neon-orange/20">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-neon-orange text-sm font-medium">💡 AI Резюме:</span>
                    </div>
                    <p className="text-sm text-gray-300">{selectedTicket.ai_summary}</p>
                  </div>
                )}
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6">
                {messages.length === 0 ? (
                  <div className="text-center py-12">
                    <span className="text-6xl opacity-20">💬</span>
                    <p className="text-gray-500 mt-4">Нет сообщений</p>
                  </div>
                ) : (
                  messages.map(message => (
                    <MessageBubble key={message.id} message={message} />
                  ))
                )}
              </div>

              {/* Info Footer */}
              <div className="p-4 border-t border-dark-border bg-dark-panel/30 backdrop-blur-sm">
                <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
                  <span>👁️</span>
                  <span>Режим мониторинга • Все ответы генерируются AI</span>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-neon-green/20 to-dark-card border border-neon-green/30 flex items-center justify-center">
                  <span className="text-5xl opacity-50">💬</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-400 mb-2">
                  Выберите тикет
                </h3>
                <p className="text-gray-600">
                  Кликните на тикет слева чтобы увидеть беседу
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
