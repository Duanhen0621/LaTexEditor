/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        primary: '#2563eb'
      },
      borderRadius: {
        lg2: '12px'
      }
    }
  },
  plugins: []
}
