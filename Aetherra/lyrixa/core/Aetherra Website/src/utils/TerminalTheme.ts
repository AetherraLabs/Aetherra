// Terminal theme configuration for retro-style terminal interface
export interface TerminalTheme {
  colors: {
    primary: string;
    secondary: string;
    background: string;
    backgroundGlow: string;
    text: string;
    textDim: string;
    textBright: string;
    cursor: string;
    selection: string;
    error: string;
    warning: string;
    success: string;
    info: string;
  };
  fonts: {
    primary: string;
    monospace: string;
    size: {
      small: string;
      medium: string;
      large: string;
    };
  };
  effects: {
    glow: {
      primary: string;
      secondary: string;
      text: string;
    };
    flicker: {
      duration: string;
      intensity: number;
    };
    scanlines: {
      opacity: number;
      spacing: string;
    };
  };
}

export const defaultTerminalTheme: TerminalTheme = {
  colors: {
    primary: '#00ff88',
    secondary: '#ff6b6b',
    background: '#0a0a0a',
    backgroundGlow: 'rgba(0, 255, 136, 0.05)',
    text: '#00ff88',
    textDim: '#4a9960',
    textBright: '#66ffaa',
    cursor: '#00ff88',
    selection: 'rgba(0, 255, 136, 0.3)',
    error: '#ff4757',
    warning: '#ffa726',
    success: '#00ff88',
    info: '#40a9ff'
  },
  fonts: {
    primary: '"JetBrains Mono", "Fira Code", "Source Code Pro", monospace',
    monospace: '"Courier New", Courier, monospace',
    size: {
      small: '12px',
      medium: '14px',
      large: '16px'
    }
  },
  effects: {
    glow: {
      primary: '0 0 10px #00ff88, 0 0 20px #00ff88, 0 0 30px #00ff88',
      secondary: '0 0 5px #ff6b6b, 0 0 10px #ff6b6b',
      text: '0 0 5px currentColor'
    },
    flicker: {
      duration: '0.15s',
      intensity: 0.95
    },
    scanlines: {
      opacity: 0.1,
      spacing: '4px'
    }
  }
};

export const cyberpunkTheme: TerminalTheme = {
  colors: {
    primary: '#ff0080',
    secondary: '#00d4ff',
    background: '#0f0015',
    backgroundGlow: 'rgba(255, 0, 128, 0.08)',
    text: '#ff0080',
    textDim: '#990040',
    textBright: '#ff40a0',
    cursor: '#ff0080',
    selection: 'rgba(255, 0, 128, 0.4)',
    error: '#ff073a',
    warning: '#ffb347',
    success: '#39ff14',
    info: '#00d4ff'
  },
  fonts: {
    primary: '"JetBrains Mono", "Fira Code", "Source Code Pro", monospace',
    monospace: '"Courier New", Courier, monospace',
    size: {
      small: '12px',
      medium: '14px',
      large: '16px'
    }
  },
  effects: {
    glow: {
      primary: '0 0 10px #ff0080, 0 0 20px #ff0080, 0 0 40px #ff0080',
      secondary: '0 0 5px #00d4ff, 0 0 15px #00d4ff',
      text: '0 0 8px currentColor, 0 0 16px currentColor'
    },
    flicker: {
      duration: '0.12s',
      intensity: 0.92
    },
    scanlines: {
      opacity: 0.15,
      spacing: '3px'
    }
  }
};

export const matrixTheme: TerminalTheme = {
  colors: {
    primary: '#00ff41',
    secondary: '#008f11',
    background: '#000000',
    backgroundGlow: 'rgba(0, 255, 65, 0.03)',
    text: '#00ff41',
    textDim: '#008f11',
    textBright: '#80ff80',
    cursor: '#00ff41',
    selection: 'rgba(0, 255, 65, 0.3)',
    error: '#ff073a',
    warning: '#ffab00',
    success: '#00ff41',
    info: '#00bcd4'
  },
  fonts: {
    primary: '"JetBrains Mono", "Fira Code", "Source Code Pro", monospace',
    monospace: '"Courier New", Courier, monospace',
    size: {
      small: '12px',
      medium: '14px',
      large: '16px'
    }
  },
  effects: {
    glow: {
      primary: '0 0 8px #00ff41, 0 0 16px #00ff41',
      secondary: '0 0 4px #008f11, 0 0 8px #008f11',
      text: '0 0 4px currentColor'
    },
    flicker: {
      duration: '0.2s',
      intensity: 0.98
    },
    scanlines: {
      opacity: 0.08,
      spacing: '2px'
    }
  }
};

// CSS utility functions for applying terminal themes
export const generateTerminalCSS = (theme: TerminalTheme): string => {
  return `
    .terminal-container {
      background: ${theme.colors.background};
      color: ${theme.colors.text};
      font-family: ${theme.fonts.primary};
      font-size: ${theme.fonts.size.medium};
      position: relative;
      overflow: hidden;
    }

    .terminal-container::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(
        transparent 50%, 
        rgba(0, 255, 136, ${theme.effects.scanlines.opacity}) 50%
      );
      background-size: 100% ${theme.effects.scanlines.spacing};
      pointer-events: none;
      z-index: 1;
    }

    .terminal-content {
      position: relative;
      z-index: 2;
      padding: 20px;
      min-height: 100vh;
    }

    .terminal-glow {
      text-shadow: ${theme.effects.glow.text};
      box-shadow: ${theme.effects.glow.primary};
    }

    .terminal-text {
      color: ${theme.colors.text};
      text-shadow: ${theme.effects.glow.text};
    }

    .terminal-text-dim {
      color: ${theme.colors.textDim};
    }

    .terminal-text-bright {
      color: ${theme.colors.textBright};
      text-shadow: ${theme.effects.glow.text};
    }

    .terminal-cursor {
      background: ${theme.colors.cursor};
      box-shadow: ${theme.effects.glow.primary};
      animation: terminal-blink 1s infinite;
    }

    .terminal-flicker {
      animation: terminal-flicker ${theme.effects.flicker.duration} infinite;
    }

    .terminal-selection {
      background: ${theme.colors.selection};
    }

    .terminal-error {
      color: ${theme.colors.error};
      text-shadow: 0 0 5px ${theme.colors.error};
    }

    .terminal-warning {
      color: ${theme.colors.warning};
      text-shadow: 0 0 5px ${theme.colors.warning};
    }

    .terminal-success {
      color: ${theme.colors.success};
      text-shadow: 0 0 5px ${theme.colors.success};
    }

    .terminal-info {
      color: ${theme.colors.info};
      text-shadow: 0 0 5px ${theme.colors.info};
    }

    @keyframes terminal-blink {
      0%, 50% { opacity: 1; }
      51%, 100% { opacity: 0; }
    }

    @keyframes terminal-flicker {
      0% { opacity: 1; }
      98% { opacity: 1; }
      99% { opacity: ${theme.effects.flicker.intensity}; }
      100% { opacity: 1; }
    }

    .terminal-input {
      background: transparent;
      border: none;
      outline: none;
      color: ${theme.colors.text};
      font-family: ${theme.fonts.primary};
      font-size: ${theme.fonts.size.medium};
      caret-color: ${theme.colors.cursor};
      text-shadow: ${theme.effects.glow.text};
    }

    .terminal-prompt {
      color: ${theme.colors.primary};
      text-shadow: ${theme.effects.glow.primary};
      font-weight: bold;
    }

    .terminal-output {
      white-space: pre-wrap;
      word-wrap: break-word;
      margin: 4px 0;
    }

    .terminal-command {
      color: ${theme.colors.textBright};
      text-shadow: ${theme.effects.glow.text};
    }

    .terminal-button {
      background: transparent;
      border: 1px solid ${theme.colors.primary};
      color: ${theme.colors.primary};
      padding: 8px 16px;
      font-family: ${theme.fonts.primary};
      font-size: ${theme.fonts.size.small};
      cursor: pointer;
      transition: all 0.3s ease;
      text-shadow: ${theme.effects.glow.text};
      box-shadow: ${theme.effects.glow.primary};
    }

    .terminal-button:hover {
      background: ${theme.colors.primary};
      color: ${theme.colors.background};
      text-shadow: none;
      box-shadow: ${theme.effects.glow.primary}, inset 0 0 10px rgba(0,0,0,0.3);
    }

    .terminal-scrollbar {
      scrollbar-width: thin;
      scrollbar-color: ${theme.colors.primary} ${theme.colors.background};
    }

    .terminal-scrollbar::-webkit-scrollbar {
      width: 8px;
    }

    .terminal-scrollbar::-webkit-scrollbar-track {
      background: ${theme.colors.background};
    }

    .terminal-scrollbar::-webkit-scrollbar-thumb {
      background: ${theme.colors.primary};
      border-radius: 4px;
      box-shadow: ${theme.effects.glow.primary};
    }

    .terminal-scrollbar::-webkit-scrollbar-thumb:hover {
      background: ${theme.colors.textBright};
    }
  `;
};

// Hook for applying terminal theme
export const useTerminalTheme = (themeName: 'default' | 'cyberpunk' | 'matrix' = 'default') => {
  const themes = {
    default: defaultTerminalTheme,
    cyberpunk: cyberpunkTheme,
    matrix: matrixTheme
  };

  const theme = themes[themeName];
  const css = generateTerminalCSS(theme);

  return { theme, css };
};

// Terminal theme configuration for specific components
export const terminalComponentStyles = {
  container: (theme: TerminalTheme) => ({
    backgroundColor: theme.colors.background,
    color: theme.colors.text,
    fontFamily: theme.fonts.primary,
    fontSize: theme.fonts.size.medium,
    textShadow: theme.effects.glow.text,
  }),

  prompt: (theme: TerminalTheme) => ({
    color: theme.colors.primary,
    textShadow: theme.effects.glow.primary,
    fontWeight: 'bold',
  }),

  input: (theme: TerminalTheme) => ({
    backgroundColor: 'transparent',
    border: 'none',
    outline: 'none',
    color: theme.colors.text,
    fontFamily: theme.fonts.primary,
    fontSize: theme.fonts.size.medium,
    caretColor: theme.colors.cursor,
    textShadow: theme.effects.glow.text,
  }),

  output: (theme: TerminalTheme) => ({
    color: theme.colors.text,
    textShadow: theme.effects.glow.text,
    whiteSpace: 'pre-wrap' as const,
    wordWrap: 'break-word' as const,
    margin: '4px 0',
  }),

  error: (theme: TerminalTheme) => ({
    color: theme.colors.error,
    textShadow: `0 0 5px ${theme.colors.error}`,
  }),

  success: (theme: TerminalTheme) => ({
    color: theme.colors.success,
    textShadow: `0 0 5px ${theme.colors.success}`,
  }),

  warning: (theme: TerminalTheme) => ({
    color: theme.colors.warning,
    textShadow: `0 0 5px ${theme.colors.warning}`,
  }),

  info: (theme: TerminalTheme) => ({
    color: theme.colors.info,
    textShadow: `0 0 5px ${theme.colors.info}`,
  }),
};
