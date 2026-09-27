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
          blue: '#0F326D',
          lightblue: '#3182CE',
          green: '#38A169',
          purple: '#805AD5',
          orange: '#DD6B20',
          bg: '#F4F7FB'
        }
      }
    },
  },
  plugins: [],
}
