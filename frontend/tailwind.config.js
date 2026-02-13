/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // TokyoNight color palette for functional theme
        'tokyo-night': '#1a1b26',
        'tokyo-bg': '#16161e',
        'tokyo-border': '#292e42',
        'tokyo-border-light': '#3b4261',
        'tokyo-fg': '#c0caf5',
        'tokyo-fg-dark': '#a9b1d6',
        'tokyo-comment': '#565f89',
        'tokyo-comment-dark': '#3b4261',
        'tokyo-blue': '#7aa2f7',
        'tokyo-cyan': '#7dcfff',
        'tokyo-green': '#9ece6a',
        'tokyo-yellow': '#e0af68',
        'tokyo-orange': '#ff9e64',
        'tokyo-red': '#f7768e',
        'tokyo-magenta': '#bb9af7',
        'tokyo-purple': '#9d7cd8',
      },
      fontFamily: {
        mono: ['Consolas', 'Fira Code', 'JetBrains Mono', 'monospace'],
        sans: ['Segoe UI', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
