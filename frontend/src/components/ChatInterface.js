import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, AlertCircle, CheckCircle } from 'lucide-react';
import { apiClient } from '../api';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: 'Hello! I\'m your AI assistant for managing doctor procedures. You can ask me to:\n\n• Show procedure history for a doctor\n• Get cost quotes for procedures\n• Add new procedures\n\nTry asking: "Show me the history for Dr. Smith" or "What is the cost for procedure TEST001?"',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(`session-${Date.now()}`);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await apiClient.chatWithAgent(inputMessage, sessionId);
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.response || response.message || 'I received your request, but got an unexpected response format.',
        timestamp: new Date(),
        success: true
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: `Sorry, I encountered an error: ${error.message}`,
        timestamp: new Date(),
        error: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTimestamp = (timestamp) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg card-shadow border border-maroon-100">
      {/* Header */}
      <div className="flex items-center p-4 bg-maroon-600 text-white rounded-t-lg maroon-shadow">
        <Bot className="w-6 h-6 mr-2" />
        <h2 className="text-lg font-semibold">AI Assistant</h2>
        <div className="ml-auto text-sm opacity-75">
          Session: {sessionId.slice(-8)}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start space-x-3 chat-message ${
              message.type === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.type === 'bot' && (
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                message.error ? 'bg-error-100' : message.success ? 'bg-success-100' : 'bg-maroon-100'
              }`}>
                {message.error ? (
                  <AlertCircle className="w-4 h-4 text-error-600" />
                ) : message.success ? (
                  <CheckCircle className="w-4 h-4 text-success-600" />
                ) : (
                  <Bot className="w-4 h-4 text-maroon-600" />
                )}
              </div>
            )}
            
            <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
              message.type === 'user'
                ? 'bg-maroon-600 text-white maroon-shadow'
                : message.error
                ? 'bg-error-50 text-error-800 border border-error-200'
                : 'bg-maroon-50 text-maroon-800 border border-maroon-100'
            }`}>
              <div className="whitespace-pre-wrap text-sm">{message.content}</div>
              <div className={`text-xs mt-1 opacity-75 ${
                message.type === 'user' ? 'text-maroon-100' : 'text-maroon-500'
              }`}>
                {formatTimestamp(message.timestamp)}
              </div>
            </div>

            {message.type === 'user' && (
              <div className="flex-shrink-0 w-8 h-8 bg-maroon-600 rounded-full flex items-center justify-center maroon-shadow">
                <User className="w-4 h-4 text-white" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex items-start space-x-3 chat-message">
            <div className="flex-shrink-0 w-8 h-8 bg-maroon-100 rounded-full flex items-center justify-center">
              <Bot className="w-4 h-4 text-maroon-600" />
            </div>
            <div className="bg-maroon-50 px-4 py-2 rounded-lg border border-maroon-100">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-maroon-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-maroon-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-maroon-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-maroon-200">
        <div className="flex space-x-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about procedures, costs, or history..."
            className="flex-1 resize-none border border-maroon-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-maroon-500 focus:border-transparent"
            rows="2"
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="px-4 py-2 bg-maroon-600 text-white rounded-lg hover:bg-maroon-700 focus:outline-none focus:ring-2 focus:ring-maroon-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center min-w-[44px] maroon-shadow"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <div className="text-xs text-maroon-500 mt-2">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
