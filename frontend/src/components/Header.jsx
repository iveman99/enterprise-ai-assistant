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
  const selected = ROLES.find(r => r.value === currentRole) || ROLES[0];

  return (
    <header style={{
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
          <div style={{
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
          {selected.label}
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
    </header>
  );
}