/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        surface: '#141414',
        border: '#1e1e1e',
      },
    },
  },
  plugins: [],
}
