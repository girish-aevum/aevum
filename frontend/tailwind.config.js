/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          primary: '#667eea',
          secondary: '#764ba2',
          dark: '#0b1220'
        }
      }
    },
  },
  plugins: [],
}; 