/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // 可爱主题色彩
        primary: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          200: '#99f6e4',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14b8a6',  // 主色 - 薄荷绿
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
        },
        cute: {
          pink: '#fce7f3',
          peach: '#fed7aa',
          lavender: '#e9d5ff',
          mint: '#d1fae5',
          sky: '#e0f2fe',
          yellow: '#fef9c3',
        },
        income: '#10b981',   // 收入绿色
        expense: '#f97316',  // 支出橙色
        // 深色模式背景色
        dark: {
          bg: '#0f172a',
          card: '#1e293b',
          border: '#334155',
        }
      },
      borderRadius: {
        'cute': '1.5rem',
        'bubble': '2rem',
      },
      boxShadow: {
        'cute': '0 4px 20px rgba(20, 184, 166, 0.15)',
        'card': '0 2px 12px rgba(0, 0, 0, 0.08)',
        'card-dark': '0 2px 12px rgba(0, 0, 0, 0.3)',
      },
      fontFamily: {
        cute: ['"Nunito"', '"PingFang SC"', '"Microsoft YaHei"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
