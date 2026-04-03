// frontend/src/App.jsx
// Main app — holds all state and wires everything together

import { useState, useEffect, useRef } from 'react';
import Header        from './components/Header';
import Sidebar       from './components/Sidebar';
import MessageBubble from './components/MessageBubble';
import InputBar      from './components/InputBar';

// ✅ UPDATED IMPORT (added streamQuery)
import { queryDocuments, getStats, streamQuery } from './services/api';

import { Bot } from 'lucide-react';


// Animations
const style = document.createElement('style');
style.textContent = `
  @keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0; }
  }
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .message-enter {
    animation: fadeIn 0.3s ease forwards;
  }
`;
document.head.appendChild(style);


export default function App() {
  const [role,     setRole]     = useState('HR');
  const [messages, setMessages] = useState([]);
  const [loading,  setLoading]  = useState(false);
  const [stats,    setStats]    = useState(null);
  const [history,  setHistory]  = useState([]);

  const bottomRef = useRef(null);


  // Load stats on mount
  useEffect(() => {
    getStats().then(setStats).catch(console.error);
  }, []);


  // Auto scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);


  // Build conversation history
  const buildHistory = () => {
    return messages.map(m => ({
      role:    m.role,
      content: m.content
    }));
  };


  // ✅ STREAMING VERSION (UPDATED)
  const handleSend = async (question) => {

    // Add user message
    const userMessage = { role: 'user', content: question };
    const conversationHistory = buildHistory();

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    // Add empty AI message (will stream into this)
    const aiMessage = {
      role:    'assistant',
      content: '',
      sources: []
    };

    setMessages(prev => [...prev, aiMessage]);
    setLoading(false); // remove loader immediately


    try {
      await streamQuery(
        question,
        role,
        conversationHistory,

        // 🟢 TOKEN STREAM
        (token) => {
          setMessages(prev => {
            const updated = [...prev];
            const last    = updated[updated.length - 1];

            updated[updated.length - 1] = {
              ...last,
              content: last.content + token
            };

            return updated;
          });
        },

        // 🟢 DONE (sources)
        (sources) => {
          setMessages(prev => {
            const updated = [...prev];
            const last    = updated[updated.length - 1];

            updated[updated.length - 1] = {
              ...last,
              sources
            };

            return updated;
          });

          // Save to sidebar history
          setHistory(prev => {
            const exists = prev.find(h => h.question === question);
            if (exists) return prev;
            return [{ question }, ...prev].slice(0, 20);
          });
        }
      );

    } catch (error) {
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role:    'assistant',
          content: '⚠️ Sorry, something went wrong. Please check the backend.',
          sources: []
        };
        return updated;
      });
    }
  };


  // History click
  const handleHistoryClick = (question) => {
    handleSend(question);
  };


  // Role change
  const handleRoleChange = (newRole) => {
    setRole(newRole);
    setMessages([]);
  };


  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>

      <Header currentRole={role} onRoleChange={handleRoleChange} />

      <div className="app-body" style={{
        display:   'flex',
        flex:      1,
        marginTop: 'var(--header-height)',
        overflow:  'hidden'
      }}>

        <Sidebar
          stats={stats}
          history={history}
          onHistoryClick={handleHistoryClick}
        />

        <main style={{
          flex:           1,
          display:        'flex',
          flexDirection:  'column',
          overflow:       'hidden',
          background:     'var(--gray-50)'
        }}>

          {/* Messages */}
          <div className="message-padding" style={{
            flex:      1,
            overflowY: 'auto',
            padding:   '24px'
          }}>

            {/* Welcome */}
            {messages.length === 0 && (
              <div style={{
                display:        'flex',
                flexDirection:  'column',
                alignItems:     'center',
                justifyContent: 'center',
                height:         '100%',
                textAlign:      'center',
                color:          'var(--gray-400)'
              }}>
                <Bot size={40} />
                <h2>Welcome to Enterprise AI</h2>
                <p>Ask questions about your documents</p>
              </div>
            )}

            {/* Messages */}
            {messages.map((msg, i) => (
              <div key={i} className="message-enter">
                <MessageBubble
                  message={msg}
                  isLatest={i === messages.length - 1}
                />
              </div>
            ))}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <InputBar
            onSend={handleSend}
            loading={loading}
            currentRole={role}
          />

        </main>
      </div>
    </div>
  );
}