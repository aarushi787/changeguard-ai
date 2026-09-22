import React from 'react';

interface McciaLogoProps {
  className?: string;
  height?: number | string;
  width?: number | string;
  theme?: 'light' | 'dark' | 'color';
  withText?: boolean;
}

export function McciaLogo({
  className = '',
  height = 36,
  theme = 'color',
  withText = false,
}: McciaLogoProps) {
  const blue = theme === 'dark' ? '#38BDF8' : '#1870B8';
  const green = '#22A848';
  const regColor = theme === 'dark' ? '#94A3B8' : '#334155';

  return (
    <div className={`mccia-brand-container ${className}`} style={{ display: 'inline-flex', alignItems: 'center', gap: '10px' }}>
      <svg
        viewBox="0 0 540 190"
        height={height}
        style={{ height, width: 'auto', display: 'block', overflow: 'visible' }}
        aria-label="MCCIA Logo"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Geometric MCCIA Logo matching exact brand typography */}
        <g id="mccia-wordmark" transform="translate(15, 20)">
          {/* 'm' */}
          <path
            fill={blue}
            d="M 5,140 L 5,35 L 35,35 L 35,55 C 42,38 56,33 72,33 C 88,33 98,40 105,55 C 114,38 128,33 145,33 L 175,33 L 175,140 L 145,140 L 145,72 C 145,58 138,52 126,52 C 114,52 108,58 108,72 L 108,140 L 78,140 L 78,72 C 78,58 71,52 59,52 C 47,52 40,58 40,72 L 40,140 Z"
          />

          {/* first 'c' */}
          <path
            fill={blue}
            d="M 252,62 L 224,73 C 218,57 206,52 192,52 C 172,52 160,68 160,88 C 160,108 172,124 192,124 C 206,124 218,119 224,103 L 252,114 C 240,136 218,144 192,144 C 152,144 130,119 130,88 C 130,57 152,32 192,32 C 218,32 240,40 252,62 Z"
          />

          {/* second 'c' */}
          <path
            fill={blue}
            d="M 334,62 L 306,73 C 300,57 288,52 274,52 C 254,52 242,68 242,88 C 242,108 254,124 274,124 C 288,124 300,119 306,103 L 334,114 C 322,136 300,144 274,144 C 234,144 212,119 212,88 C 212,57 234,32 274,32 C 300,32 322,40 334,62 Z"
          />

          {/* 'i' */}
          <path
            fill={blue}
            d="M 350,35 L 380,35 L 380,140 L 350,140 Z"
          />

          {/* 'a' (Green) */}
          <path
            fill={green}
            d="M 450,35 L 480,35 L 480,140 L 452,140 L 452,125 C 442,138 425,144 405,144 C 375,144 355,125 355,92 C 355,59 380,48 420,48 L 450,48 L 450,46 C 450,38 440,32 425,32 C 410,32 398,37 392,46 L 372,30 C 385,15 408,12 430,12 C 458,12 480,24 480,55 L 480,140 L 450,140 Z M 450,70 L 425,70 C 402,70 388,78 388,94 C 388,110 400,122 418,122 C 438,122 450,110 450,92 Z"
          />

          {/* Registered trademark ® */}
          <g transform="translate(488, 12)">
            <circle cx="9" cy="9" r="8" fill="none" stroke={regColor} strokeWidth="1.8" />
            <text
              x="9"
              y="12.5"
              fontFamily="'Segoe UI', Arial, sans-serif"
              fontSize="9"
              fontWeight="bold"
              textAnchor="middle"
              fill={regColor}
            >
              R
            </text>
          </g>
        </g>
      </svg>
      {withText && (
        <div style={{ lineHeight: 1.15 }}>
          <div style={{ fontWeight: 700, fontSize: '15px', letterSpacing: '-0.3px', color: theme === 'dark' ? '#FFFFFF' : '#0B2238' }}>
            Review <span style={{ color: green }}>Desk</span>
          </div>
          <div style={{ fontSize: '9px', fontWeight: 600, letterSpacing: '1px', color: theme === 'dark' ? '#94A3B8' : '#1870B8' }}>
            MCCIA AI APPLIED STUDIO
          </div>
        </div>
      )}
    </div>
  );
}

export default McciaLogo;
