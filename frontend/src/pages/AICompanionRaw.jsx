import React, { useRef, useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { FaMagic, FaUserCircle, FaPaperPlane, FaRobot } from 'react-icons/fa';
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
              <span className="text-green-500 mt-1">•</span>
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
  'Explain quantum computing',
  'Write a short story about AI',
  'Discuss the future of technology',
  'Explain a complex scientific concept',
  'Help me brainstorm project ideas'
];

function AICompanionRaw() {
  const [messages, setMessages] = useState([
    { sender: 'ai', text: 'Hi! I am your Raw AI Companion. Ask me anything without summarization.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (text) => {
    if (!text.trim()) return;
    setInput('');
    setLoading(true);
    try {
      // Send message to raw AI companion endpoint
      const chatRes = await apiClient.post('/ai-companion/ai-companion-raw/', {
        text: text
      });

      // Add user and AI messages from response
      setMessages(msgs => [
        ...msgs,
        { sender: 'user', text: text },
        { sender: 'ai', text: chatRes.data.text }
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
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-green-100 dark:from-gray-900 dark:via-gray-900 dark:to-green-900 flex flex-col">
      <Navbar />
      <main className="flex-grow container mx-auto px-4 py-8 flex flex-col items-center justify-center">
        <div className="max-w-2xl w-full bg-white/90 dark:bg-gray-800/90 rounded-3xl shadow-2xl p-0 flex flex-col border border-green-100 dark:border-green-800 backdrop-blur-xl">
          {/* Header */}
          <div className="flex flex-col items-center pt-10 pb-4 px-8 border-b border-green-100 dark:border-green-800">
            <FaMagic className="text-green-500 text-5xl mb-2" />
            <h1 className="text-3xl font-extrabold text-green-700 mb-1 text-center tracking-tight">AI Companion</h1>
            <p className="text-base text-gray-500 dark:text-gray-300 text-center mb-2">
              Unfiltered AI responses without summarization.
            </p>
          </div>
          {/* Smart Suggestions */}
          <div className="flex flex-wrap gap-2 justify-center px-8 py-4 bg-green-50 dark:bg-green-900/30 border-b border-green-100 dark:border-green-800">
            {SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                className="px-4 py-2 bg-green-100 dark:bg-green-800 text-green-700 dark:text-green-200 rounded-full text-sm font-medium shadow hover:bg-green-200 dark:hover:bg-green-700 transition-colors"
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
                    <div className="bg-green-100 dark:bg-green-800 text-green-900 dark:text-green-100 rounded-2xl px-4 py-2 shadow max-w-xs">
                      <FormattedText text={msg.text} />
                    </div>
                    <FaRobot className="text-green-400 text-xl mb-1" />
                  </div>
                )}
                {msg.sender === 'user' && (
                  <div className="flex items-end gap-2">
                    <FaUserCircle className="text-gray-400 text-2xl mb-1" />
                    <div className="bg-green-500 text-white rounded-2xl px-4 py-2 shadow max-w-xs whitespace-pre-line">
                      {String(msg.text || '')}
                    </div>
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-green-100 dark:bg-green-800 text-green-900 dark:text-green-100 rounded-2xl px-4 py-2 shadow max-w-xs flex items-center gap-2 animate-pulse">
                  <span className="inline-block w-2 h-2 bg-green-400 rounded-full animate-bounce" />
                  <span className="inline-block w-2 h-2 bg-green-300 rounded-full animate-bounce delay-100" />
                  <span className="inline-block w-2 h-2 bg-green-200 rounded-full animate-bounce delay-200" />
                </div>
                <FaRobot className="text-green-400 text-xl mb-1 ml-2" />
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
          {/* Input Bar */}
          <form
            className="flex items-center gap-2 px-6 py-4 border-t border-green-100 dark:border-green-800 bg-white/80 dark:bg-gray-900/80 rounded-b-3xl"
            onSubmit={e => { e.preventDefault(); handleSend(input); }}
          >
            <textarea
              className="flex-1 resize-none rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-2 focus:outline-none focus:ring-2 focus:ring-green-400 text-base min-h-[40px] max-h-[120px]"
              placeholder="Type your message..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleInputKeyDown}
              rows={1}
              disabled={loading}
            />
            <button
              type="submit"
              className="p-3 rounded-full bg-green-500 hover:bg-green-600 text-white shadow transition-colors disabled:opacity-50"
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

export default AICompanionRaw; 