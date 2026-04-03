// frontend/src/components/Sidebar.jsx
// Left sidebar — system stats + conversation history

import { FileText, Database, MessageSquare, Clock } from 'lucide-react';

export default function Sidebar({ stats, history, onHistoryClick }) {
  return (
    <aside className="sidebar-container" style={{
      width:      'var(--sidebar-width)',
      background: 'var(--white)',
      borderRight:'1px solid var(--gray-200)',
      height:     '100%',
      overflowY:  'auto',
      padding:    '20px 0',
      flexShrink: 0
    }}>

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