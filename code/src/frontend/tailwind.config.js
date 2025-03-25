/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      './pages/**/*.{js,ts,jsx,tsx,mdx}',
      './components/**/*.{js,ts,jsx,tsx,mdx}',
      './app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
      extend: {
        keyframes: {
          'fade-in': {
            '0%': { opacity: '0', transform: 'translateY(-1rem)' },
            '100%': { opacity: '1', transform: 'translateY(0)' }
          }
        },
        animation: {
          'fade-in': 'fade-in 0.2s ease-out'
        }
      },
    },
    plugins: [],
  }; 