import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useChat } from '../hooks/useChat';

export const ChatPage: React.FC = () => {
  const { matchId } = useParams<{ matchId: string }>();
  const navigate = useNavigate();
  const [inputText, setInputText] = useState('');
  
  const currentUserId = Number(localStorage.getItem('userId')) || 1; 
  const parsedMatchId = Number(matchId);

  const { 
    messages, 
    sendMessage, 
    isLoadingHistory, 
    isConnected,
    loadMoreMessages,
    hasMore
  } = useChat(parsedMatchId, currentUserId);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const chatContainerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    sendMessage(inputText);
    setInputText('');
  };

  if (isLoadingHistory) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <p className="text-gray-500 animate-pulse font-medium">Загрузка истории переписки...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Верхняя панель (Header) */}
      <header className="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200 shadow-sm z-10">
        <div className="flex items-center space-x-3">
          <button 
            onClick={() => navigate('/matches')} 
            className="text-gray-600 hover:text-black transition font-medium text-sm"
          >
            ← К матчам
          </button>
          <h2 className="text-base font-semibold text-gray-800">Диалог #{matchId}</h2>
        </div>
        
        {/* Статус сокета */}
        <div className="flex items-center space-x-2 bg-gray-100 px-3 py-1.5 rounded-full">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-amber-500 animate-pulse'}`} />
          <span className="text-xs font-medium text-gray-600">
            {isConnected ? 'В сети' : 'Подключение...'}
          </span>
        </div>
      </header>

      {/* Область сообщений */}
      <div 
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50"
      >
        {/* Кнопка подгрузки истории (показывается, если есть что грузить) */}
        {hasMore && (
          <div className="text-center pb-2">
            <button 
              type="button"
              onClick={loadMoreMessages}
              className="text-xs text-blue-600 hover:text-blue-700 bg-white border border-gray-200 px-4 py-2 rounded-full shadow-sm font-medium transition"
            >
              Показать более старые сообщения
            </button>
          </div>
        )}

        {messages.map((msg) => {
          const isMe = msg.sender_id === currentUserId;
          return (
            <div 
              key={msg.id} 
              className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`max-w-xs md:max-w-md px-4 py-2.5 rounded-2xl shadow-sm ${
                  isMe 
                    ? 'bg-blue-600 text-white rounded-br-none' 
                    : 'bg-white text-gray-800 rounded-bl-none border border-gray-100'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap break-words">{msg.content}</p>
                
                {/* Время отправки */}
                <span className={`block text-[10px] text-right mt-1 font-light ${isMe ? 'text-blue-200' : 'text-gray-400'}`}>
                  {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          );
        })}
        
        {/* Вспомогательный div для автоскролла */}
        <div ref={messagesEndRef} />
      </div>

      {/* Нижняя панель ввода (Footer) */}
      <footer className="p-4 bg-white border-t border-gray-200 shadow-inner">
        <form onSubmit={handleSend} className="flex space-x-3 max-w-4xl mx-auto">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={isConnected ? "Напишите сообщение..." : "Соединение разорвано..."}
            disabled={!isConnected}
            maxLength={4000}
            className="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white disabled:bg-gray-100 disabled:cursor-not-allowed text-sm text-gray-900 shadow-sm transition-all"
          />
          <button
            type="submit"
            disabled={!inputText.trim() || !isConnected}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-xl shadow-sm transition"
          >
            Отправить
          </button>
        </form>
      </footer>
    </div>
  );
};
