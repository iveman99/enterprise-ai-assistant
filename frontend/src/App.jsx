// frontend/src/App.jsx
// Main app — holds all state and wires everything together

import { useState, useEffect, useRef } from 'react';
import Header      from './components/Header';
import Sidebar     from './components/Sidebar';
import MessageBubble from './components/MessageBubble';
import InputBar    from './components/InputBar';
import { queryDocuments, getStats } from './services/api';
import { Bot } from 'lucide-react';

// Add keyframe animations to document
const style = document.createElement('style');
style.textContent = `
  @keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0; }
  }
  @keyframes spin {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
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

  // Scroll to bottom when messages update
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Build conversation history for API
  // Format: [{role: "user", content: "..."}, {role: "assistant", content: "..."}]
  const buildHistory = () => {
    return messages.map(m => ({
      role:    m.role,
      content: m.content
    }));
  };

  const handleSend = async (question) => {
    // Add user message immediately
    const userMessage = { role: 'user', content: question };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const conversationHistory = buildHistory();

      const result = await queryDocuments(
        question,
        role,
        conversationHistory
      );

      // Add AI response
      const aiMessage = {
        role:    'assistant',
        content: result.answer,
        sources: result.sources
      };

      setMessages(prev => [...prev, aiMessage]);

      // Add to sidebar history (avoid duplicates)
      setHistory(prev => {
        const exists = prev.find(h => h.question === question);
        if (exists) return prev;
        return [{ question }, ...prev].slice(0, 20);
      });

    } catch (error) {
      setMessages(prev => [...prev, {
        role:    'assistant',
        content: '⚠️ Sorry, something went wrong. Please check the backend is running and try again.',
        sources: []
      }]);
    }

    setLoading(false);
  };

  // When user clicks a history item — prefill as new question
  const handleHistoryClick = (question) => {
    handleSend(question);
  };

  // When role changes — clear chat and start fresh
  const handleRoleChange = (newRole) => {
    setRole(newRole);
    setMessages([]);
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>

      {/* Fixed header */}
      <Header currentRole={role} onRoleChange={handleRoleChange} />

      {/* Main content below header */}
      <div style={{
        display:   'flex',
        flex:      1,
        marginTop: 'var(--header-height)',
        overflow:  'hidden'
      }}>

        {/* Sidebar */}
        <Sidebar
          stats={stats}
          history={history}
          onHistoryClick={handleHistoryClick}
        />

        {/* Chat area */}
        <main style={{
          flex:           1,
          display:        'flex',
          flexDirection:  'column',
          overflow:       'hidden',
          background:     'var(--gray-50)'
        }}>

          {/* Messages */}
          <div style={{
            flex:      1,
            overflowY: 'auto',
            padding:   '24px'
          }}>

            {/* Welcome screen */}
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
                <div style={{
                  width:          64,
                  height:         64,
                  borderRadius:   '50%',
                  background:     'var(--primary-light)',
                  display:        'flex',
                  alignItems:     'center',
                  justifyContent: 'center',
                  marginBottom:   16
                }}>
                  <Bot size={28} color="var(--primary)" />
                </div>
                <h2 style={{
                  fontSize:     20,
                  fontWeight:   600,
                  color:        'var(--gray-700)',
                  marginBottom: 8
                }}>
                  Welcome to Enterprise AI
                </h2>
                <p style={{ fontSize: 14, maxWidth: 400, lineHeight: 1.6 }}>
                  Ask any question about your company documents.
                  I'll find the most relevant information and cite my sources.
                </p>
                <div style={{
                  display:   'flex',
                  gap:       8,
                  marginTop: 24,
                  flexWrap:  'wrap',
                  justifyContent: 'center'
                }}>
                  {[
                    'What is the leave policy?',
                    'How does budget approval work?',
                    'What are the IT security standards?'
                  ].map(q => (
                    <button
                      key={q}
                      onClick={() => handleSend(q)}
                      style={{
                        padding:      '8px 14px',
                        background:   'var(--white)',
                        border:       '1px solid var(--gray-200)',
                        borderRadius: 'var(--radius-md)',
                        fontSize:     13,
                        color:        'var(--gray-600)',
                        cursor:       'pointer',
                        transition:   'all 0.15s'
                      }}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Chat messages */}
            {messages.map((msg, i) => (
              <div key={i} className="message-enter">
                <MessageBubble
                  message={msg}
                  isLatest={i === messages.length - 1}
                />
              </div>
            ))}

            {/* Loading indicator */}
            {loading && (
              <div style={{
                display:    'flex',
                gap:        12,
                alignItems: 'flex-start',
                marginBottom: 24
              }}>
                <div style={{
                  width:          36,
                  height:         36,
                  borderRadius:   '50%',
                  background:     'var(--gray-100)',
                  border:         '1px solid var(--gray-200)',
                  display:        'flex',
                  alignItems:     'center',
                  justifyContent: 'center'
                }}>
                  <Bot size={16} color="var(--primary)" />
                </div>
                <div style={{
                  padding:      '12px 16px',
                  background:   'var(--white)',
                  border:       '1px solid var(--gray-200)',
                  borderRadius: 'var(--radius-sm) var(--radius-lg) var(--radius-lg) var(--radius-lg)',
                  display:      'flex',
                  gap:          6,
                  alignItems:   'center'
                }}>
                  {[0, 1, 2].map(i => (
                    <div key={i} style={{
                      width:       8,
                      height:      8,
                      borderRadius:'50%',
                      background:  'var(--primary)',
                      animation:   `blink 1.2s ease-in-out ${i * 0.2}s infinite`
                    }} />
                  ))}
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input bar — fixed at bottom */}
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