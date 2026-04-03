// frontend/src/components/MessageBubble.jsx
// Single chat message — user or AI
// AI messages have typing animation + source cards

import { useState, useEffect } from 'react';
import { User, Bot, Copy, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import SourceCards from './SourceCards';

// Copy Button Component
function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 4,
        marginTop: 6,
        padding: '4px 10px',
        background: 'transparent',
        border: '1px solid var(--gray-200)',
        borderRadius: 'var(--radius-sm)',
        cursor: 'pointer',
        fontSize: 11,
        color: 'var(--gray-400)',
        transition: 'all 0.15s'
      }}
    >
      {copied ? (
        <>
          <Check size={11} color="var(--success)" />
          <span style={{ color: 'var(--success)' }}>Copied!</span>
        </>
      ) : (
        <>
          <Copy size={11} />
          Copy answer
        </>
      )}
    </button>
  );
}

// Typing animation
function TypingText({ text, onDone }) {
  const [displayed, setDisplayed] = useState('');
  const [done, setDone] = useState(false);

  useEffect(() => {
    let i = 0;
    const timer = setInterval(() => {
      if (i < text.length) {
        setDisplayed(text.slice(0, i + 1));
        i++;
      } else {
        clearInterval(timer);
        setDone(true);
        if (onDone) onDone();
      }
    }, 8);

    return () => clearInterval(timer);
  }, [text]);

  return (
    <div className="markdown-body">
      <ReactMarkdown>{displayed}</ReactMarkdown>

      {!done && (
        <span
          style={{
            display: 'inline-block',
            width: 2,
            height: 16,
            background: 'var(--primary)',
            marginLeft: 2,
            animation: 'blink 1s infinite'
          }}
        />
      )}
    </div>
  );
}

export default function MessageBubble({ message, isLatest }) {
  const isUser = message.role === 'user';
  const [typingDone, setTypingDone] = useState(!isLatest || isUser);

  return (
    <div
      style={{
        display: 'flex',
        gap: 12,
        marginBottom: 24,
        flexDirection: isUser ? 'row-reverse' : 'row',
        alignItems: 'flex-start'
      }}
    >
      {/* Avatar */}
      <div
        style={{
          width: 36,
          height: 36,
          borderRadius: '50%',
          background: isUser ? 'var(--primary)' : 'var(--gray-100)',
          border: isUser ? 'none' : '1px solid var(--gray-200)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0
        }}
      >
        {isUser ? (
          <User size={16} color="white" />
        ) : (
          <Bot size={16} color="var(--primary)" />
        )}
      </div>

      {/* Content */}
      <div style={{ maxWidth: '75%', minWidth: 0 }}>
        {/* Label */}
        <p
          style={{
            fontSize: 11,
            fontWeight: 600,
            color: 'var(--gray-400)',
            marginBottom: 6,
            textAlign: isUser ? 'right' : 'left',
            textTransform: 'uppercase',
            letterSpacing: '0.05em'
          }}
        >
          {isUser ? 'You' : 'AI Assistant'}
        </p>

        {/* Bubble */}
        <div
          style={{
            padding: '12px 16px',
            background: isUser ? 'var(--primary)' : 'var(--white)',
            color: isUser ? 'white' : 'var(--gray-800)',
            borderRadius: isUser
              ? 'var(--radius-lg) var(--radius-sm) var(--radius-lg) var(--radius-lg)'
              : 'var(--radius-sm) var(--radius-lg) var(--radius-lg) var(--radius-lg)',
            border: isUser ? 'none' : '1px solid var(--gray-200)',
            boxShadow: 'var(--shadow-sm)',
            fontSize: 14,
            lineHeight: 1.7
          }}
        >
          {isUser ? (
            <p>{message.content}</p>
          ) : isLatest ? (
            <TypingText
              text={message.content}
              onDone={() => setTypingDone(true)}
            />
          ) : (
            <ReactMarkdown>{message.content}</ReactMarkdown>
          )}
        </div>

        {/* Copy button */}
        {!isUser && typingDone && (
          <CopyButton text={message.content} />
        )}

        {/* ✅ FINAL FIX — Source Cards Logic */}
        {!isUser &&
          typingDone &&
          message.sources &&
          message.sources.length > 0 &&
          !message.content.includes("I could not find") &&
          !message.content.includes("Hello! 👋") &&
          !message.content.includes("document access summary") &&
          !message.content.includes("I'm your Enterprise AI") && (
            <div style={{ marginTop: 8 }}>
              <SourceCards sources={message.sources} />
            </div>
          )}
      </div>
    </div>
  );
}