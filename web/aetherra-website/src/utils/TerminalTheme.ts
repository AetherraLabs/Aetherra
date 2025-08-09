export const terminalThemes = {
    aether: {
        primary: '#00ff41',
        secondary: '#008f11',
        background: '#000000',
        surface: '#0a0a0a',
        accent: '#00ff88',
        error: '#ff0040',
        warning: '#ffaa00',
        info: '#00aaff',
        text: '#00ff41',
        muted: '#666666',
        cursor: '#00ff41',
        selection: 'rgba(0, 255, 65, 0.3)'
    },
    matrix: {
        primary: '#00ff00',
        secondary: '#008800',
        background: '#000000',
        surface: '#001100',
        accent: '#44ff44',
        error: '#ff4444',
        warning: '#ffff44',
        info: '#4444ff',
        text: '#00ff00',
        muted: '#555555',
        cursor: '#00ff00',
        selection: 'rgba(0, 255, 0, 0.3)'
    },
    cyberpunk: {
        primary: '#ff00ff',
        secondary: '#aa00aa',
        background: '#000011',
        surface: '#110022',
        accent: '#00ffff',
        error: '#ff0066',
        warning: '#ffaa00',
        info: '#0088ff',
        text: '#ff00ff',
        muted: '#666688',
        cursor: '#ff00ff',
        selection: 'rgba(255, 0, 255, 0.3)'
    },
    amber: {
        primary: '#ffb000',
        secondary: '#cc8800',
        background: '#1a0f00',
        surface: '#2a1800',
        accent: '#ffd700',
        error: '#ff6600',
        warning: '#ff9900',
        info: '#66aaff',
        text: '#ffb000',
        muted: '#996600',
        cursor: '#ffb000',
        selection: 'rgba(255, 176, 0, 0.3)'
    },
    consciousness: {
        primary: '#00ddff',
        secondary: '#0088aa',
        background: '#000814',
        surface: '#001122',
        accent: '#88ddff',
        error: '#ff4466',
        warning: '#ffcc44',
        info: '#44aaff',
        text: '#00ddff',
        muted: '#4488aa',
        cursor: '#00ddff',
        selection: 'rgba(0, 221, 255, 0.3)'
    }
};

export const terminalFonts = {
    classic: {
        fontFamily: '"Courier New", Courier, monospace',
        fontSize: '14px',
        lineHeight: '1.4',
        letterSpacing: '0.5px'
    },
    modern: {
        fontFamily: '"Fira Code", "JetBrains Mono", monospace',
        fontSize: '14px',
        lineHeight: '1.5',
        letterSpacing: '0px'
    },
    retro: {
        fontFamily: '"VT323", "Perfect DOS VGA 437", monospace',
        fontSize: '16px',
        lineHeight: '1.2',
        letterSpacing: '1px'
    },
    hacker: {
        fontFamily: '"Share Tech Mono", "Anonymous Pro", monospace',
        fontSize: '13px',
        lineHeight: '1.4',
        letterSpacing: '0.3px'
    }
};

export const terminalEffects = {
    none: {},
    glow: {
        textShadow: '0 0 5px currentColor, 0 0 10px currentColor, 0 0 15px currentColor',
        filter: 'brightness(1.1)'
    },
    flicker: {
        animation: 'flicker 0.15s infinite linear alternate'
    },
    scanlines: {
        background: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.03) 2px, rgba(255,255,255,0.03) 4px)',
        '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'linear-gradient(transparent 50%, rgba(0,255,0,0.03) 50%)',
            backgroundSize: '100% 4px',
            pointerEvents: 'none'
        }
    },
    crt: {
        borderRadius: '10px',
        filter: 'contrast(1.1) brightness(1.1)',
        '&::after': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.3) 100%)',
            pointerEvents: 'none'
        }
    }
};

export const keyframes = `
@keyframes flicker {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

@keyframes cursor-blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

@keyframes glow-pulse {
  0%, 100% { filter: brightness(1) drop-shadow(0 0 5px currentColor); }
  50% { filter: brightness(1.2) drop-shadow(0 0 10px currentColor); }
}

@keyframes scan-lines {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100vh); }
}

@keyframes data-stream {
  0% { transform: translateY(-100px); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { transform: translateY(100vh); opacity: 0; }
}

@keyframes terminal-boot {
  0% { width: 0; }
  50% { width: 100%; }
  100% { width: 100%; opacity: 1; }
}

@keyframes consciousness-pulse {
  0%, 100% {
    background: radial-gradient(ellipse at center, rgba(0,221,255,0.1) 0%, rgba(0,0,0,0.9) 70%);
    transform: scale(1);
  }
  50% {
    background: radial-gradient(ellipse at center, rgba(0,221,255,0.2) 0%, rgba(0,0,0,0.8) 70%);
    transform: scale(1.02);
  }
}
`;

export type TerminalTheme = keyof typeof terminalThemes;
export type TerminalFont = keyof typeof terminalFonts;
export type TerminalEffect = keyof typeof terminalEffects;

export interface TerminalStyleConfig {
    theme: TerminalTheme;
    font: TerminalFont;
    effects: TerminalEffect[];
    customCss?: string;
}

export const getTerminalStyles = (config: TerminalStyleConfig) => {
    const theme = terminalThemes[config.theme];
    const font = terminalFonts[config.font];
    const effects = config.effects.map(effect => terminalEffects[effect]);

    return {
        ...font,
        color: theme.text,
        backgroundColor: theme.background,
        ...effects.reduce((acc, effect) => ({ ...acc, ...effect }), {}),
        ...(config.customCss ? { style: config.customCss } : {})
    };
};

export const defaultTerminalConfig: TerminalStyleConfig = {
    theme: 'aether',
    font: 'modern',
    effects: ['glow', 'scanlines'],
    customCss: ''
};

// Predefined configurations for different experiences
export const terminalPresets = {
    aetherDefault: {
        theme: 'aether' as TerminalTheme,
        font: 'modern' as TerminalFont,
        effects: ['glow', 'scanlines'] as TerminalEffect[],
        customCss: 'border: 1px solid rgba(0, 255, 65, 0.3);'
    },
    matrixMode: {
        theme: 'matrix' as TerminalTheme,
        font: 'retro' as TerminalFont,
        effects: ['glow', 'flicker', 'scanlines'] as TerminalEffect[],
        customCss: 'border: 1px solid rgba(0, 255, 0, 0.5);'
    },
    cyberpunkHacker: {
        theme: 'cyberpunk' as TerminalTheme,
        font: 'hacker' as TerminalFont,
        effects: ['glow', 'crt'] as TerminalEffect[],
        customCss: 'border: 1px solid rgba(255, 0, 255, 0.4);'
    },
    retroAmber: {
        theme: 'amber' as TerminalTheme,
        font: 'classic' as TerminalFont,
        effects: ['glow'] as TerminalEffect[],
        customCss: 'border: 1px solid rgba(255, 176, 0, 0.3);'
    },
    consciousnessMode: {
        theme: 'consciousness' as TerminalTheme,
        font: 'modern' as TerminalFont,
        effects: ['glow', 'scanlines'] as TerminalEffect[],
        customCss: 'border: 1px solid rgba(0, 221, 255, 0.4); animation: consciousness-pulse 3s ease-in-out infinite;'
    }
};

export const applyTerminalTheme = (element: HTMLElement, config: TerminalStyleConfig) => {
    const styles = getTerminalStyles(config);

    Object.entries(styles).forEach(([property, value]) => {
        if (property === 'style') return;
        element.style.setProperty(property.replace(/([A-Z])/g, '-$1').toLowerCase(), value as string);
    });

    // Add keyframe animations to document if not already present
    if (!document.getElementById('terminal-keyframes')) {
        const style = document.createElement('style');
        style.id = 'terminal-keyframes';
        style.textContent = keyframes;
        document.head.appendChild(style);
    }
};

export const getThemeCSS = (config: TerminalStyleConfig) => {
    const theme = terminalThemes[config.theme];
    const font = terminalFonts[config.font];

    return `
    .terminal-${config.theme} {
      font-family: ${font.fontFamily};
      font-size: ${font.fontSize};
      line-height: ${font.lineHeight};
      letter-spacing: ${font.letterSpacing};
      color: ${theme.text};
      background-color: ${theme.background};
      border-color: ${theme.primary};
    }

    .terminal-${config.theme} .terminal-cursor {
      color: ${theme.cursor};
      animation: cursor-blink 1.2s infinite;
    }

    .terminal-${config.theme} .terminal-input {
      color: ${theme.primary};
      text-shadow: 0 0 5px ${theme.primary};
    }

    .terminal-${config.theme} .terminal-output {
      color: ${theme.accent};
    }

    .terminal-${config.theme} .terminal-error {
      color: ${theme.error};
      text-shadow: 0 0 5px ${theme.error};
    }

    .terminal-${config.theme} .terminal-warning {
      color: ${theme.warning};
    }

    .terminal-${config.theme} .terminal-info {
      color: ${theme.info};
    }

    .terminal-${config.theme} .terminal-muted {
      color: ${theme.muted};
    }

    .terminal-${config.theme}::selection {
      background: ${theme.selection};
    }
  `;
};
