import { useEffect, useRef, useState, useCallback } from 'react';

interface WebSocketHook {
  lastMessage: MessageEvent | null;
  sendMessage: (message: string) => void;
  isConnected: boolean;
}

export const useWebSocket = (url: string): WebSocketHook => {
  const [lastMessage, setLastMessage] = useState<MessageEvent | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    const connect = () => {
      console.log('[WebSocket] Attempting to connect to:', url);
      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        console.log('[WebSocket] Connected successfully to:', url);
        setIsConnected(true);
      };

      ws.current.onclose = () => {
        console.log('[WebSocket] Disconnected from:', url);
        setIsConnected(false);
        // Attempt to reconnect after 5 seconds
        setTimeout(connect, 5000);
      };

      ws.current.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
      };

      ws.current.onmessage = (event) => {
        console.log('[WebSocket] Message received:', event.data.substring(0, 10) + '...');
        setLastMessage(event);
      };
    };

    connect();

    return () => {
      if (ws.current) {
        console.log('[WebSocket] Closing connection to:', url);
        ws.current.close();
      }
    };
  }, [url]);

  const sendMessage = useCallback((message: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      console.log('[WebSocket] Sending message:', message);
      ws.current.send(message);
    } else {
      console.warn('[WebSocket] Cannot send message - not connected');
    }
  }, []);

  return { lastMessage, sendMessage, isConnected };
}; 