import type { Config } from 'tailwindcss'

// Tokens come from docs/05-ui-ux-specification.md. Values live as CSS variables in
// src/styles/index.css so a future theme only has to redefine the variables.
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-primary)',
        'text-primary': 'var(--color-text-primary)',
        'text-muted': 'var(--color-text-muted)',
        surface: 'var(--color-surface)',
        bg: 'var(--color-bg)',
        border: 'var(--color-border)',
        sidebar: {
          DEFAULT: 'var(--color-sidebar)',
          text: 'var(--color-sidebar-text)',
          active: 'var(--color-sidebar-active)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      fontSize: { base: ['14px', '1.5'] },
      spacing: { xs: '4px', sm: '8px', md: '12px', lg: '16px', xl: '24px', '2xl': '32px' },
      borderRadius: { sm: '6px', md: '10px', lg: '12px', xl: '16px' },
      boxShadow: {
        card: '0 2px 8px rgba(0,0,0,0.05)',
        button: '0 1px 3px rgba(0,0,0,0.1)',
      },
      maxWidth: { content: '1440px' },
    },
  },
  plugins: [],
} satisfies Config
