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
  const [isMobileNavOpen, setMobileNavOpen] = useState(false);
  const [activeModal, setActiveModal] = useState(null);

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

      <Header currentRole={role} onRoleChange={handleRoleChange} onToggleNav={() => setMobileNavOpen(p => !p)} onOpenModal={setActiveModal} />

      {/* Mobile Sidebar Overlay */}
      {isMobileNavOpen && (
        <div 
          className="mobile-overlay" 
          onClick={() => setMobileNavOpen(false)} 
        />
      )}

      {/* CEO Presentation Modals (Overview / Future) */}
      {activeModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.6)', zIndex: 9999,
          display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20,
          backdropFilter: 'blur(4px)'
        }}>
          <div style={{
            background: 'white', width: '100%', maxWidth: 650, borderRadius: 'var(--radius-lg)',
            padding: '32px 40px', position: 'relative', boxShadow: 'var(--shadow-xl)',
            maxHeight: '90vh', overflowY: 'auto'
          }}>
            <button 
              onClick={() => setActiveModal(null)}
              style={{ position: 'absolute', top: 16, right: 20, background: 'none', border: 'none', cursor: 'pointer', fontSize: 24, color: 'var(--gray-500)' }}
            >
              ✕
            </button>
            
            {activeModal === 'current' ? (
              <>
                <h2 style={{ marginTop: 0, color: 'var(--gray-900)', fontSize: 24, marginBottom: 12 }}>Current System Capabilities</h2>
                <p style={{ color: 'var(--gray-600)', fontSize: 15, lineHeight: 1.6, marginBottom: 24 }}>
                  Right now, the Enterprise Assistant acts as a secure, smart search engine for our internal company documents.
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                  <div><strong style={{ color: 'var(--gray-900)', fontSize: 16 }}>🔒 Security First (RBAC)</strong><br/><span style={{ color: 'var(--gray-600)' }}>It identifies who is asking (e.g., HR vs Finance) and completely blocks access to unauthorized documents.</span></div>
                  <div><strong style={{ color: 'var(--gray-900)', fontSize: 16 }}>⚡ Instant Analysis</strong><br/><span style={{ color: 'var(--gray-600)' }}>Instead of employees manually reading through dozens of PDFs, the system instantly reads all permitted documents and extracts exact answers.</span></div>
                  <div><strong style={{ color: 'var(--gray-900)', fontSize: 16 }}>📝 Grounded Fact-Checking</strong><br/><span style={{ color: 'var(--gray-600)' }}>It provides a verifiable 'Source' link for every claim it makes, ensuring leadership always knows exactly which policy page an answer came from.</span></div>
                  <div><strong style={{ color: 'var(--gray-900)', fontSize: 16 }}>🧠 Contextual Memory</strong><br/><span style={{ color: 'var(--gray-600)' }}>It remembers what you asked five minutes ago, so you can have a natural, continuous follow-up conversation without repeating context.</span></div>
                </div>
              </>
            ) : (
              <>
                <h2 style={{ marginTop: 0, color: 'var(--primary)', fontSize: 24, marginBottom: 12 }}>Future Enhancements & Vision</h2>
                <p style={{ color: 'var(--gray-600)', fontSize: 15, lineHeight: 1.6, marginBottom: 24 }}>
                  While currently a powerful "read-only" search engine, our roadmap evolves this into an active, automated AI Agent.
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                  <div><strong style={{ color: 'var(--gray-900)', fontSize: 16 }}>🚀 Taking Action (Agent Mode)</strong><br/><span style={{ color: 'var(--gray-600)' }}>Instead of just explaining the vacation policy, the assistant will automatically open HR software APIs and submit the time-off request on your behalf.</span></div>
                  <div><strong style={{ color: 'var(--gray-900)', fontSize: 16 }}>📊 Excel & Data Crunching</strong><br/><span style={{ color: 'var(--gray-600)' }}>Upgrading the vector-engine to process complex tabular (Excel) sheets, allowing executives to ask <em>"What was our total quarterly spend?"</em> and get instant mathematical breakdowns.</span></div>
                  <div><strong style={{ color: 'var(--gray-900)', fontSize: 16 }}>✉️ Automated Reporting</strong><br/><span style={{ color: 'var(--gray-600)' }}>The system will proactively gather weekly metrics from different departments and draft summary emails or reports for leadership review automatically.</span></div>
                  <div><strong style={{ color: 'var(--gray-900)', fontSize: 16 }}>📱 Voice & Mobile Ecosystem</strong><br/><span style={{ color: 'var(--gray-600)' }}>Expanding the tool into a secured mobile app interface so executives and employees can ask questions via voice while commuting or away from their desk.</span></div>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      <div className="app-body" style={{
        display:   'flex',
        flex:      1,
        marginTop: 'var(--header-height)',
        overflow:  'hidden'
      }}>

        <Sidebar
          stats={stats}
          history={history}
          onHistoryClick={(q) => {
            handleHistoryClick(q);
            setMobileNavOpen(false);
          }}
          isOpen={isMobileNavOpen}
          onOpenModal={(modalType) => {
            setActiveModal(modalType);
            setMobileNavOpen(false); // Close slider when modal pops
          }}
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