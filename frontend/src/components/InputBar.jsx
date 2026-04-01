// frontend/src/components/InputBar.jsx
// Question input + send button at the bottom

import { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';

export default function InputBar({ onSend, loading, currentRole }) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim() || loading) return;
    onSend(input.trim());
    setInput('');
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{
      padding:    '16px 24px',
      background: 'var(--white)',
      borderTop:  '1px solid var(--gray-200)'
    }}>

      {/* Role indicator */}
      <p style={{
        fontSize:     12,
        color:        'var(--gray-400)',
        marginBottom: 8,
        textAlign:    'center'
      }}>
        Searching as <strong style={{ color: 'var(--primary)' }}>{currentRole}</strong> — only accessible documents will be searched
      </p>

      <div style={{
        display:      'flex',
        gap:          10,
        alignItems:   'flex-end',
        background:   'var(--gray-50)',
        border:       '1px solid var(--gray-200)',
        borderRadius: 'var(--radius-lg)',
        padding:      '8px 8px 8px 16px',
        transition:   'border-color 0.15s',
      }}>
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder={`Ask anything about ${currentRole} department documents...`}
          rows={1}
          style={{
            flex:       1,
            border:     'none',
            background: 'transparent',
            resize:     'none',
            fontSize:   14,
            color:      'var(--gray-800)',
            outline:    'none',
            fontFamily: 'Inter, sans-serif',
            lineHeight: 1.5,
            maxHeight:  120,
            overflowY:  'auto'
          }}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || loading}
          style={{
            width:          38,
            height:         38,
            borderRadius:   'var(--radius-md)',
            background:     input.trim() && !loading
                            ? 'var(--primary)'
                            : 'var(--gray-200)',
            border:         'none',
            cursor:         input.trim() && !loading ? 'pointer' : 'not-allowed',
            display:        'flex',
            alignItems:     'center',
            justifyContent: 'center',
            transition:     'background 0.15s',
            flexShrink:     0
          }}
        >
          {loading
            ? <Loader2 size={16} color="white" style={{ animation: 'spin 1s linear infinite' }} />
            : <Send size={16} color={input.trim() ? 'white' : 'var(--gray-400)'} />
          }
        </button>
      </div>
    </div>
  );
}