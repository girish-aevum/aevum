import React, { useRef, useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { FaMagic, FaUserCircle, FaMicrophone, FaPaperPlane, FaRobot } from 'react-icons/fa';
import apiClient from '../apiClient';

// Simple text formatter that converts basic markdown to styled text
const FormattedText = ({ text }) => {
  const safeText = typeof text === 'string' ? text : String(text || '');
  
  // Split by lines and process each line
  const lines = safeText.split('\n');
  
  return (
    <div className="space-y-2">
      {lines.map((line, index) => {
        // Handle bullet points
        if (line.trim().startsWith('* ')) {
          const content = line.replace(/^\* /, '');
          const formattedContent = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
          
          return (
            <div key={index} className="flex items-start gap-2">
              <span className="text-blue-500 mt-1">•</span>
              <span dangerouslySetInnerHTML={{ __html: formattedContent }} />
            </div>
          );
        }
        
        // Handle bold and italic text in regular lines
        const formattedLine = line
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Skip empty lines
        if (!line.trim()) {
          return <div key={index} className="h-2" />;
        }
        
        return (
          <div key={index} dangerouslySetInnerHTML={{ __html: formattedLine }} />
        );
      })}
    </div>
  );
};

const SUGGESTIONS = [
  'How can I improve my sleep?',
  'Suggest a healthy meal',
  'Give me a daily wellness tip',
  'Summarize my recent journal',
  'How do I reduce stress?'
];

function AICompanion() {
  const [messages, setMessages] = useState([
    { sender: 'ai', text: 'Hi! I am your AI Companion. How can I help you today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [threadId, setThreadId] = useState(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (text) => {
    if (!text.trim()) return;
    setInput('');
    setLoading(true);
    try {
      let currentThreadId = threadId;
      // If no thread, create one with the message as the title
      if (!currentThreadId) {
        const threadRes = await apiClient.post('/ai-companion/threads/', {
          title: text.slice(0, 50),
          category: 'MENTAL_HEALTH',
        });
        currentThreadId = threadRes.data.thread_id;
        setThreadId(currentThreadId);
      }
      // Send message to chat endpoint
      const chatRes = await apiClient.post('/ai-companion/chat/', {
        thread_id: currentThreadId,
        message: text,
      });
      // Add user and AI messages from response (no duplicate user message)
      setMessages(msgs => [
        ...msgs,
        { sender: 'user', text: chatRes.data.user_message.content },
        { sender: 'ai', text: chatRes.data.ai_response.content }
      ]);
    } catch (err) {
      setMessages(msgs => [
        ...msgs,
        { sender: 'ai', text: 'Sorry, something went wrong. Please try again.' }
      ]);
    }
    setLoading(false);
  };

  const handleSuggestion = (suggestion) => {
    setInput(suggestion);
    handleSend(suggestion);
  };

  const handleInputKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(input);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100 dark:from-gray-900 dark:via-gray-900 dark:to-blue-900 flex flex-col">
      <Navbar />
      <main className="flex-grow container mx-auto px-4 py-8 flex flex-col items-center justify-center">
        <div className="max-w-2xl w-full bg-white/90 dark:bg-gray-800/90 rounded-3xl shadow-2xl p-0 flex flex-col border border-blue-100 dark:border-blue-800 backdrop-blur-xl">
          {/* Header */}
          <div className="flex flex-col items-center pt-10 pb-4 px-8 border-b border-blue-100 dark:border-blue-800">
            <FaMagic className="text-blue-500 text-5xl mb-2" />
            <h1 className="text-3xl font-extrabold text-blue-700 mb-1 text-center tracking-tight drop-shadow">AI Companion</h1>
            <p className="text-base text-gray-500 dark:text-gray-300 text-center mb-2">
              Your personal AI assistant for health, wellness, and more.
            </p>
          </div>
          {/* Smart Suggestions */}
          <div className="flex flex-wrap gap-2 justify-center px-8 py-4 bg-blue-50 dark:bg-blue-900/30 border-b border-blue-100 dark:border-blue-800">
            {SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                className="px-4 py-2 bg-blue-100 dark:bg-blue-800 text-blue-700 dark:text-blue-200 rounded-full text-sm font-medium shadow hover:bg-blue-200 dark:hover:bg-blue-700 transition-colors"
                onClick={() => handleSuggestion(s)}
              >
                {s}
              </button>
            ))}
          </div>
          {/* Chat Area */}
          <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4 min-h-[300px] max-h-[50vh]" style={{scrollbarWidth: 'thin'}}>
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.sender === 'ai' && (
                  <div className="flex items-end gap-2">
                                          <div className="bg-blue-100 dark:bg-blue-800 text-blue-900 dark:text-blue-100 rounded-2xl px-4 py-2 shadow max-w-xs">
                        <FormattedText text={msg.text} />
                      </div>
                    <FaRobot className="text-blue-400 text-xl mb-1" />
                  </div>
                )}
                {msg.sender === 'user' && (
                  <div className="flex items-end gap-2">
                    <FaUserCircle className="text-gray-400 text-2xl mb-1" />
                    <div className="bg-blue-500 text-white rounded-2xl px-4 py-2 shadow max-w-xs whitespace-pre-line">
                      {String(msg.text || '')}
                    </div>
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-blue-100 dark:bg-blue-800 text-blue-900 dark:text-blue-100 rounded-2xl px-4 py-2 shadow max-w-xs flex items-center gap-2 animate-pulse">
                  <span className="inline-block w-2 h-2 bg-blue-400 rounded-full animate-bounce" />
                  <span className="inline-block w-2 h-2 bg-blue-300 rounded-full animate-bounce delay-100" />
                  <span className="inline-block w-2 h-2 bg-blue-200 rounded-full animate-bounce delay-200" />
                </div>
                <FaRobot className="text-blue-400 text-xl mb-1 ml-2" />
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
          {/* Input Bar */}
          <form
            className="flex items-center gap-2 px-6 py-4 border-t border-blue-100 dark:border-blue-800 bg-white/80 dark:bg-gray-900/80 rounded-b-3xl"
            onSubmit={e => { e.preventDefault(); handleSend(input); }}
          >
            <textarea
              className="flex-1 resize-none rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400 text-base min-h-[40px] max-h-[120px]"
              placeholder="Type your message..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleInputKeyDown}
              rows={1}
              disabled={loading}
            />
            <button
              type="submit"
              className="p-3 rounded-full bg-blue-500 hover:bg-blue-600 text-white shadow transition-colors disabled:opacity-50"
              disabled={loading || !input.trim()}
              aria-label="Send"
            >
              <FaPaperPlane className="text-lg" />
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}

export default AICompanion; 