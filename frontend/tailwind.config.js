/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        maroon: {
          50: '#fef8f8',
          100: '#fdf0f0',
          200: '#fad7d7',
          300: '#f5b5b5',
          400: '#ec8888',
          500: '#df5a5a',
          600: '#c41e3a',
          700: '#a0142a',
          800: '#800020',
          900: '#660019',
        },
        primary: {
          50: '#fef8f8',
          100: '#fdf0f0',
          500: '#800020',
          600: '#a0142a',
          700: '#c41e3a',
        },
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e',
          600: '#16a34a',
        },
        warning: {
          50: '#fefce8',
          100: '#fef3c7',
          500: '#eab308',
          600: '#ca8a04',
        },
        error: {
          50: '#fef2f2',
          100: '#fee2e2',
          500: '#ef4444',
          600: '#dc2626',
        }
      }
    },
  },
  plugins: [],
}
