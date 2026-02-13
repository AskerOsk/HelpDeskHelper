/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'neon-green': '#00FF41',
        'neon-orange': '#FF6B35',
        'dark-bg': '#000000',
        'dark-panel': '#0A0A0A',
        'dark-card': '#141414',
        'dark-border': '#1F1F1F',
        'dark-hover': '#1A1A1A',
      },
      backdropBlur: {
        'xs': '2px',
      },
      boxShadow: {
        'neon-green': '0 0 20px rgba(0, 255, 65, 0.3)',
        'neon-orange': '0 0 20px rgba(255, 107, 53, 0.3)',
        'glow-green': '0 0 40px rgba(0, 255, 65, 0.4), 0 0 80px rgba(0, 255, 65, 0.2)',
        'glow-orange': '0 0 40px rgba(255, 107, 53, 0.4), 0 0 80px rgba(255, 107, 53, 0.2)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 20px rgba(0, 255, 65, 0.3)' },
          '100%': { boxShadow: '0 0 40px rgba(0, 255, 65, 0.6), 0 0 80px rgba(0, 255, 65, 0.3)' },
        }
      }
    },
  },
  plugins: [],
}

