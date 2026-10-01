/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          orange: '#FF5500',
          'orange-hover': '#FF7722',
          dark: '#0D0D0E',
          card: '#161618',
          border: '#26262A',
        }
      }
    },
  },
  plugins: [],
}
