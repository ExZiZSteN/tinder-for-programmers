import { useEffect, useRef, useState, useCallback } from 'react';
import { chatApi, Message } from '../api/chat';


const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

export const useChat = (matchId: number, currentUserId: number) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState<boolean>(true);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [hasMore, setHasMore] = useState<boolean>(true);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectDelayRef = useRef<number>(1000);


  const getToken = () => localStorage.getItem('token') || '';

  const loadInitialHistory = useCallback(async () => {
    try {
      setIsLoadingHistory(true);
      const history = await chatApi.getMessages(matchId, undefined, 30);
      

      setMessages(history.reverse());
      
      if (history.length < 30) {
        setHasMore(false);
      }
    } catch (error) {
      console.error('Ошибка при загрузке начальной истории чата:', error);
    } finally {
      setIsLoadingHistory(false);
    }
  }, [matchId]);


  const loadMoreMessages = useCallback(async () => {
    if (messages.length === 0 || !hasMore) return;
    
    try {
      const firstMessageId = messages[0].id;
      const olderMessages = await chatApi.getMessages(matchId, firstMessageId, 30);
      
      if (olderMessages.length < 30) {
        setHasMore(false);
      }
      
      if (olderMessages.length > 0) {

        setMessages((prev) => [...olderMessages.reverse(), ...prev]);
      }
    } catch (error) {
      console.error('Ошибка при подгрузке старых сообщений:', error);
    }
  }, [messages, matchId, hasMore]);


  const connectWS = useCallback(() => {
    if (wsRef.current) return;

    const token = getToken();

    const ws = new WebSocket(`${WS_URL}/ws/chat/${matchId}?token=${token}`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log(`Успешно подключено к WebSocket чата: ${matchId}`);
      setIsConnected(true);
      reconnectDelayRef.current = 1000;
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        
        if (msg.type === 'message') {
          setMessages((prev) => {

            const isDuplicate = prev.some((existingMsg) => existingMsg.id === msg.id);
            if (isDuplicate) return prev;
            return [...prev, msg];
          });
        }
      } catch (err) {
        console.error('Ошибка парсинга сообщения от сервера:', err);
      }
    };

    ws.onclose = (event) => {
      setIsConnected(false);
      wsRef.current = null;
      console.warn(`WebSocket закрыт (код: ${event.code}).`);

      if (event.code !== 4001 && event.code !== 4003 && event.code !== 4004) {
        reconnectTimeoutRef.current = setTimeout(() => {

          reconnectDelayRef.current = Math.min(reconnectDelayRef.current * 2, 30000);
          connectWS();
        }, reconnectDelayRef.current);
      }
    };

    ws.onerror = (error) => {
      console.error('Ошибка WebSocket:', error);
      ws.close();
    };
  }, [matchId]);


  useEffect(() => {
    loadInitialHistory();
    connectWS();

    return () => {

      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [matchId, loadInitialHistory, connectWS]);


  const sendMessage = useCallback((content: string) => {
    if (!content.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return;
    }

    const payload = {
      type: 'message',
      content: content.trim(),
    };

    wsRef.current.send(JSON.stringify(payload));
  }, []);

  return { 
    messages, 
    sendMessage, 
    isLoadingHistory, 
    isConnected, 
    loadMoreMessages, 
    hasMore 
  };
};
