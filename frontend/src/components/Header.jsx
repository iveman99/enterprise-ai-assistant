// frontend/src/components/Header.jsx
// Top bar — logo, title, role switcher

import { Building2, ChevronDown } from 'lucide-react';
import { useState } from 'react';

const ROLES = [
  { value: 'HR',               label: 'HR Employee',       color: '#10b981' },
  { value: 'Finance',          label: 'Finance Analyst',   color: '#f59e0b' },
  { value: 'IT',               label: 'IT Engineer',       color: '#3b82f6' },
  { value: 'Legal',            label: 'Legal Counsel',     color: '#8b5cf6' },
  { value: 'Operations',       label: 'Operations Manager',color: '#ef4444' },
  { value: 'Executive',        label: 'Executive (All)',   color: '#0f172a' },
];

export default function Header({ currentRole, onRoleChange }) {
  const [open, setOpen] = useState(false);
  const [modal, setModal] = useState(null);
  const selected = ROLES.find(r => r.value === currentRole) || ROLES[0];

  return (
    <header className="header-container" style={{
      height:          'var(--header-height)',
      background:      'var(--white)',
      borderBottom:    '1px solid var(--gray-200)',
      display:         'flex',
      alignItems:      'center',
      justifyContent:  'space-between',
      padding:         '0 24px',
      position:        'fixed',
      top:             0,
      left:            0,
      right:           0,
      zIndex:          100,
      boxShadow:       'var(--shadow-sm)'
    }}>

      {/* Logo + Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <div style={{
          width:          38,
          height:         38,
          background:     'var(--primary)',
          borderRadius:   'var(--radius-md)',
          display:        'flex',
          alignItems:     'center',
          justifyContent: 'center'
        }}>
          <Building2 size={20} color="white" />
        </div>
        <div>
          <div style={{
            fontWeight:  700,
            fontSize:    15,
            color:       'var(--gray-900)',
            lineHeight:  1.2
          }}>
            Enterprise AI
          </div>
          <div className="header-title-sub" style={{
            fontSize:  11,
            color:     'var(--gray-400)',
            fontWeight: 500,
            letterSpacing: '0.05em',
            textTransform: 'uppercase'
          }}>
            Knowledge Assistant
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {/* CEO Navigation Buttons */}
        <div className="header-nav-buttons" style={{ display: 'flex', gap: 8 }}>
          <button
            onClick={() => setModal('current')}
            style={{
              background: 'transparent', border: '1px solid var(--primary)', color: 'var(--primary)',
              padding: '6px 12px', borderRadius: 'var(--radius-md)', fontSize: 13, fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s'
            }}
          >
            System Overview
          </button>
          <button
            onClick={() => setModal('future')}
            style={{
              background: 'var(--primary)', border: 'none', color: 'white',
              padding: '6px 12px', borderRadius: 'var(--radius-md)', fontSize: 13, fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s'
            }}
          >
            Future Vision
          </button>
        </div>

        {/* Role Switcher */}
        <div style={{ position: 'relative' }}>
        <button
          onClick={() => setOpen(!open)}
          style={{
            display:      'flex',
            alignItems:   'center',
            gap:          8,
            padding:      '8px 14px',
            background:   'var(--gray-50)',
            border:       '1px solid var(--gray-200)',
            borderRadius: 'var(--radius-md)',
            cursor:       'pointer',
            fontSize:     14,
            fontWeight:   500,
            color:        'var(--gray-700)',
            transition:   'all 0.15s'
          }}
        >
          {/* Role color dot */}
          <span style={{
            width:        8,
            height:       8,
            borderRadius: '50%',
            background:   selected.color,
            display:      'inline-block'
          }} />
          <span className="role-label">{selected.label}</span>
          <ChevronDown size={14} color="var(--gray-400)" />
        </button>

        {/* Dropdown */}
        {open && (
          <div style={{
            position:     'absolute',
            top:          'calc(100% + 6px)',
            right:        0,
            background:   'var(--white)',
            border:       '1px solid var(--gray-200)',
            borderRadius: 'var(--radius-md)',
            boxShadow:    'var(--shadow-lg)',
            minWidth:     200,
            overflow:     'hidden',
            zIndex:       200
          }}>
            {ROLES.map(role => (
              <button
                key={role.value}
                onClick={() => {
                  onRoleChange(role.value);
                  setOpen(false);
                }}
                style={{
                  display:    'flex',
                  alignItems: 'center',
                  gap:        10,
                  width:      '100%',
                  padding:    '10px 16px',
                  background: role.value === currentRole
                              ? 'var(--primary-light)'
                              : 'transparent',
                  border:     'none',
                  cursor:     'pointer',
                  fontSize:   14,
                  color:      role.value === currentRole
                              ? 'var(--primary)'
                              : 'var(--gray-700)',
                  textAlign:  'left',
                  fontWeight: role.value === currentRole ? 600 : 400,
                  transition: 'background 0.1s'
                }}
              >
                <span style={{
                  width:        8,
                  height:       8,
                  borderRadius: '50%',
                  background:   role.color,
                  flexShrink:   0
                }} />
                {role.label}
              </button>
            ))}
          </div>
        )}
        </div>
      </div>

      {/* Modal Overlay */}
      {modal && (
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
              onClick={() => setModal(null)}
              style={{ position: 'absolute', top: 16, right: 20, background: 'none', border: 'none', cursor: 'pointer', fontSize: 24, color: 'var(--gray-500)' }}
            >
              ✕
            </button>
            
            {modal === 'current' ? (
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
    </header>
  );
}