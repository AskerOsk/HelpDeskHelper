import { useState, useEffect } from 'react';

const BACKEND_URL = 'http://localhost:3001';

function App() {
  const [tickets, setTickets] = useState([]);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [managerId, setManagerId] = useState(localStorage.getItem('managerId') || '');
  const [managerName, setManagerName] = useState(localStorage.getItem('managerName') || '');
  const [showLogin, setShowLogin] = useState(!localStorage.getItem('managerId'));

  // Загрузка списка тикетов
  useEffect(() => {
    fetchTickets();
    const interval = setInterval(fetchTickets, 5000); // Обновление каждые 5 секунд
    return () => clearInterval(interval);
  }, []);

  // Загрузка сообщений выбранного тикета
  useEffect(() => {
    if (selectedTicket) {
      fetchMessages(selectedTicket.id);
      const interval = setInterval(() => fetchMessages(selectedTicket.id), 3000);
      return () => clearInterval(interval);
    }
  }, [selectedTicket]);

  const fetchTickets = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/tickets`);
      const data = await response.json();
      setTickets(data);
    } catch (error) {
      console.error('Error fetching tickets:', error);
    }
  };

  const fetchMessages = async (ticketId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/tickets/${ticketId}`);
      const data = await response.json();
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedTicket) return;

    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/tickets/${selectedTicket.id}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          senderType: 'manager',
          senderId: managerId,
          content: newMessage
        })
      });

      if (response.ok) {
        setNewMessage('');
        await fetchMessages(selectedTicket.id);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateTicketStatus = async (ticketId, status) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/tickets/${ticketId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });

      if (response.ok) {
        await fetchTickets();
        if (selectedTicket?.id === ticketId) {
          setSelectedTicket({ ...selectedTicket, status });
        }
      }
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      new: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      resolved: 'bg-green-100 text-green-800',
      closed: 'bg-gray-100 text-gray-800'
    };
    
    const labels = {
      new: 'Новый',
      in_progress: 'В работе',
      resolved: 'Решен',
      closed: 'Закрыт'
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || styles.new}`}>
        {labels[status] || status}
      </span>
    );
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleLogin = (e) => {
    e.preventDefault();
    if (managerId.trim() && managerName.trim()) {
      localStorage.setItem('managerId', managerId);
      localStorage.setItem('managerName', managerName);
      setShowLogin(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('managerId');
    localStorage.removeItem('managerName');
    setManagerId('');
    setManagerName('');
    setShowLogin(true);
  };

  // Форма входа
  if (showLogin) {
    return (
      <div className="flex h-screen bg-gray-100 items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
          <h1 className="text-2xl font-bold mb-6 text-center text-blue-600">Sulpak HelpDesk</h1>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ID Менеджера
              </label>
              <input
                type="text"
                value={managerId}
                onChange={(e) => setManagerId(e.target.value)}
                placeholder="Например: manager_1"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Имя
              </label>
              <input
                type="text"
                value={managerName}
                onChange={(e) => setManagerName(e.target.value)}
                placeholder="Ваше имя"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Войти
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Левая панель - список тикетов */}
      <div className="w-1/3 bg-white border-r border-gray-200 overflow-y-auto">
        <div className="p-4 border-b border-gray-200 bg-blue-600 text-white">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-xl font-bold">Sulpak HelpDesk</h1>
              <p className="text-sm opacity-90">👤 {managerName}</p>
            </div>
            <button
              onClick={handleLogout}
              className="text-sm bg-blue-700 hover:bg-blue-800 px-3 py-1 rounded transition-colors"
            >
              Выйти
            </button>
          </div>
        </div>

        <div className="p-2">
          {tickets.length === 0 ? (
            <p className="text-center text-gray-500 py-8">Нет тикетов</p>
          ) : (
            tickets.map(ticket => (
              <div
                key={ticket.id}
                onClick={() => setSelectedTicket(ticket)}
                className={`p-4 mb-2 rounded-lg cursor-pointer transition-colors ${
                  selectedTicket?.id === ticket.id
                    ? 'bg-blue-50 border-2 border-blue-500'
                    : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="font-semibold text-sm text-gray-700">
                    #{ticket.ticket_number}
                  </span>
                  {getStatusBadge(ticket.status)}
                </div>
                
                <p className="text-sm text-gray-600 mb-2">
                  @{ticket.telegram_username || 'Unknown'}
                </p>
                
                {ticket.first_message && (
                  <p className="text-sm text-gray-800 line-clamp-2">
                    {ticket.first_message}
                  </p>
                )}
                
                <p className="text-xs text-gray-500 mt-2">
                  {formatDate(ticket.created_at)}
                </p>
                
                {ticket.message_count > 0 && (
                  <div className="mt-2 text-xs text-blue-600">
                    💬 {ticket.message_count} сообщений
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Правая панель - переписка */}
      <div className="flex-1 flex flex-col">
        {selectedTicket ? (
          <>
            {/* Заголовок тикета */}
            <div className="p-4 bg-white border-b border-gray-200">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-lg font-semibold">
                    Тикет #{selectedTicket.ticket_number}
                  </h2>
                  <p className="text-sm text-gray-600">
                    @{selectedTicket.telegram_username}
                  </p>
                </div>
                
                <div className="flex gap-2">
                  <select
                    value={selectedTicket.status}
                    onChange={(e) => updateTicketStatus(selectedTicket.id, e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="new">Новый</option>
                    <option value="in_progress">В работе</option>
                    <option value="resolved">Решен</option>
                    <option value="closed">Закрыт</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Сообщения */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${msg.sender_type === 'manager' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      msg.sender_type === 'manager'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-800'
                    }`}
                  >
                    <p className="text-sm font-medium mb-1">
                      {msg.sender_type === 'manager' ? 'Менеджер' : 'Клиент'}
                    </p>

                    {/* Отображение медиа если есть */}
                    {msg.media_type && msg.media_url && (
                      <div className="mb-2">
                        {msg.media_type === 'photo' && (
                          <img
                            src={msg.media_url}
                            alt="Фото от клиента"
                            className="rounded-lg max-w-full h-auto cursor-pointer hover:opacity-90 transition"
                            onClick={() => window.open(msg.media_url, '_blank')}
                          />
                        )}
                        {msg.media_type === 'video' && (
                          <video
                            controls
                            className="rounded-lg max-w-full h-auto"
                            src={msg.media_url}
                          >
                            Ваш браузер не поддерживает видео.
                          </video>
                        )}
                      </div>
                    )}

                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    <p className="text-xs opacity-75 mt-1">
                      {formatDate(msg.created_at)}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Форма отправки сообщения */}
            <div className="p-4 bg-white border-t border-gray-200">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Введите сообщение..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={loading}
                />
                <button
                  onClick={sendMessage}
                  disabled={loading || !newMessage.trim()}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? 'Отправка...' : 'Отправить'}
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <p className="text-lg">Выберите тикет для просмотра переписки</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

