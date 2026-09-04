import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        bg: 'var(--color-bg)', 'bg-soft': 'var(--color-bg-soft)', surface: 'var(--color-surface)',
        'surface-soft': 'var(--color-surface-soft)', border: 'var(--color-border)', 'border-strong': 'var(--color-border-strong)',
        text: 'var(--color-text)', 'text-secondary': 'var(--color-text-secondary)', 'text-tertiary': 'var(--color-text-tertiary)',
        accent: 'var(--color-accent)', 'accent-hover': 'var(--color-accent-hover)', 'accent-active': 'var(--color-accent-active)',
        'accent-soft': 'var(--color-accent-soft)', 'on-accent': 'var(--color-on-accent)', link: 'var(--color-link)',
        success: 'var(--color-success)', warning: 'var(--color-warning)', danger: 'var(--color-danger)', 'danger-soft': 'var(--color-danger-soft)',
      },
      fontFamily: { ui: ['-apple-system','BlinkMacSystemFont','SF Pro Text','PingFang SC','Microsoft YaHei','system-ui','sans-serif'], mono: ['ui-monospace','SFMono-Regular','Menlo','Consolas','monospace'] },
      fontSize: { xs: '12px', sm: '13px', base: '15px', lg: '17px', xl: '20px', '2xl': '28px', '3xl': '34px' },
      fontWeight: { regular: '400', medium: '500', semibold: '600' },
      lineHeight: { tight: '1.25', normal: '1.5' },
      spacing: { xs: '4px', sm: '8px', md: '12px', lg: '16px', xl: '20px', '2xl': '24px', '3xl': '32px' },
      borderRadius: { sm: '6px', md: '10px', lg: '14px', pill: '999px' },
      borderWidth: { hairline: '1px' },
      boxShadow: { card: 'var(--shadow-card)' },
      maxWidth: { content: '980px' },
      minHeight: { touch: '44px' }, minWidth: { touch: '44px' },
      transitionDuration: { fast: '120ms', base: '200ms', slow: '300ms' },
      transitionTimingFunction: { standard: 'cubic-bezier(0.4, 0, 0.2, 1)' },
    },
  },
  plugins: [],
} satisfies Config
