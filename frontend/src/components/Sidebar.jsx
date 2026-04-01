// frontend/src/components/Sidebar.jsx
// Left sidebar — system stats + conversation history

import { FileText, Database, MessageSquare, Clock } from 'lucide-react';

export default function Sidebar({ stats, history, onHistoryClick }) {
  return (
    <aside style={{
      width:      'var(--sidebar-width)',
      background: 'var(--white)',
      borderRight:'1px solid var(--gray-200)',
      height:     '100%',
      overflowY:  'auto',
      padding:    '20px 0',
      flexShrink: 0
    }}>

      {/* Stats Section */}
      <div style={{ padding: '0 16px 20px', borderBottom: '1px solid var(--gray-100)' }}>
        <p style={{
          fontSize:      11,
          fontWeight:    600,
          color:         'var(--gray-400)',
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          marginBottom:  12
        }}>
          System Status
        </p>

        {/* Docs count */}
        <div style={{
          display:      'flex',
          alignItems:   'center',
          gap:          10,
          padding:      '10px 12px',
          background:   'var(--primary-light)',
          borderRadius: 'var(--radius-md)',
          marginBottom: 8
        }}>
          <FileText size={16} color="var(--primary)" />
          <div>
            <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--primary)', lineHeight: 1 }}>
              42
            </div>
            <div style={{ fontSize: 11, color: 'var(--gray-500)', marginTop: 2 }}>
              Documents loaded
            </div>
          </div>
        </div>

        {/* Chunks count */}
        <div style={{
          display:      'flex',
          alignItems:   'center',
          gap:          10,
          padding:      '10px 12px',
          background:   'var(--success-light)',
          borderRadius: 'var(--radius-md)',
          marginBottom: 8
        }}>
          <Database size={16} color="var(--success)" />
          <div>
            <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--success)', lineHeight: 1 }}>
              {stats?.total_chunks || 1193}
            </div>
            <div style={{ fontSize: 11, color: 'var(--gray-500)', marginTop: 2 }}>
              Searchable chunks
            </div>
          </div>
        </div>

        {/* Departments */}
        <div style={{
          display:      'flex',
          alignItems:   'center',
          gap:          10,
          padding:      '10px 12px',
          background:   'var(--warning-light)',
          borderRadius: 'var(--radius-md)'
        }}>
          <MessageSquare size={16} color="var(--warning)" />
          <div>
            <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--warning)', lineHeight: 1 }}>
              5
            </div>
            <div style={{ fontSize: 11, color: 'var(--gray-500)', marginTop: 2 }}>
              Departments indexed
            </div>
          </div>
        </div>
      </div>

      {/* Conversation History */}
      <div style={{ padding: '20px 16px 0' }}>
        <p style={{
          fontSize:      11,
          fontWeight:    600,
          color:         'var(--gray-400)',
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          marginBottom:  12
        }}>
          Recent Questions
        </p>

        {history.length === 0 ? (
          <div style={{
            textAlign:  'center',
            padding:    '24px 12px',
            color:      'var(--gray-400)',
            fontSize:   13
          }}>
            <Clock size={24} style={{ marginBottom: 8, opacity: 0.5 }} />
            <p>No questions yet.</p>
            <p>Start by asking something!</p>
          </div>
        ) : (
          history.map((item, index) => (
            <button
              key={index}
              onClick={() => onHistoryClick(item.question)}
              style={{
                display:      'block',
                width:        '100%',
                textAlign:    'left',
                padding:      '8px 12px',
                marginBottom: 4,
                background:   'transparent',
                border:       '1px solid var(--gray-200)',
                borderRadius: 'var(--radius-sm)',
                cursor:       'pointer',
                fontSize:     13,
                color:        'var(--gray-600)',
                whiteSpace:   'nowrap',
                overflow:     'hidden',
                textOverflow: 'ellipsis',
                transition:   'all 0.15s'
              }}
              onMouseEnter={e => e.target.style.background = 'var(--gray-50)'}
              onMouseLeave={e => e.target.style.background = 'transparent'}
            >
              {item.question}
            </button>
          ))
        )}
      </div>
    </aside>
  );
}