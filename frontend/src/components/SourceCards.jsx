// frontend/src/components/SourceCards.jsx
// Citation cards shown below each AI answer

import { FileText, Building2 } from 'lucide-react';

const DEPT_COLORS = {
  HR:         { bg: '#ecfdf5', color: '#10b981', border: '#a7f3d0' },
  Finance:    { bg: '#fffbeb', color: '#f59e0b', border: '#fcd34d' },
  IT:         { bg: '#eff6ff', color: '#3b82f6', border: '#bfdbfe' },
  Legal:      { bg: '#f5f3ff', color: '#8b5cf6', border: '#ddd6fe' },
  Operations: { bg: '#fff1f2', color: '#ef4444', border: '#fecdd3' },
};

export default function SourceCards({ sources }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div style={{ marginTop: 12 }}>
      <p style={{
        fontSize:   11,
        fontWeight: 600,
        color:      'var(--gray-400)',
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
        marginBottom: 8
      }}>
        Sources
      </p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
        {sources.map((source, i) => {
          const colors = DEPT_COLORS[source.department] || DEPT_COLORS.HR;
          const score  = Math.round(source.score * 100);

          return (
            <div
              key={i}
              style={{
                display:      'flex',
                alignItems:   'center',
                gap:          8,
                padding:      '8px 12px',
                background:   colors.bg,
                border:       `1px solid ${colors.border}`,
                borderRadius: 'var(--radius-md)',
                maxWidth:     280
              }}
            >
              <FileText size={14} color={colors.color} style={{ flexShrink: 0 }} />
              <div style={{ minWidth: 0 }}>
                <div style={{
                  fontSize:     13,
                  fontWeight:   500,
                  color:        'var(--gray-800)',
                  whiteSpace:   'nowrap',
                  overflow:     'hidden',
                  textOverflow: 'ellipsis'
                }}>
                  {source.filename}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 2 }}>
                  <span style={{
                    fontSize:     11,
                    color:        colors.color,
                    fontWeight:   600,
                    background:   'white',
                    padding:      '1px 6px',
                    borderRadius: 4
                  }}>
                    {source.department}
                  </span>
                  <span style={{ fontSize: 11, color: 'var(--gray-400)' }}>
                    {score}% match
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}