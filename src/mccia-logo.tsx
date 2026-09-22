import React from 'react';

interface McciaLogoProps {
  className?: string;
  height?: number | string;
  theme?: 'light' | 'dark' | 'color';
  withText?: boolean;
}

export function McciaLogo({
  className = '',
  height = 32,
  theme = 'color',
  withText = false,
}: McciaLogoProps) {
  const numericHeight = typeof height === 'number' ? height : parseInt(String(height), 10) || 32;

  return (
    <div
      className={`mccia-brand-mark ${className}`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '10px',
      }}
    >
      <div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: theme === 'dark' ? '#FFFFFF' : 'transparent',
          padding: theme === 'dark' ? '4px 8px' : '0',
          borderRadius: theme === 'dark' ? '6px' : '0',
          boxShadow: theme === 'dark' ? '0 2px 8px rgba(0,0,0,0.18)' : 'none',
        }}
      >
        <img
          src="/mccia-logo.png"
          alt="MCCIA - Mahratta Chamber of Commerce, Industries and Agriculture"
          style={{
            height: numericHeight,
            width: 'auto',
            display: 'block',
            objectFit: 'contain',
          }}
          onError={(e) => {
            // Fallback to SVG if PNG fails to load
            (e.currentTarget as HTMLElement).style.display = 'none';
          }}
        />
      </div>
      {withText && (
        <div style={{ lineHeight: 1.15 }}>
          <div
            style={{
              fontWeight: 700,
              fontSize: '15px',
              letterSpacing: '-0.3px',
              color: theme === 'dark' ? '#FFFFFF' : '#0B2238',
            }}
          >
            Review <span style={{ color: '#21A14B' }}>Desk</span>
          </div>
          <div
            style={{
              fontSize: '8.5px',
              fontWeight: 700,
              letterSpacing: '0.8px',
              color: theme === 'dark' ? '#94A3B8' : '#1D66A8',
            }}
          >
            AI APPLIED STUDIO
          </div>
        </div>
      )}
    </div>
  );
}

export default McciaLogo;
