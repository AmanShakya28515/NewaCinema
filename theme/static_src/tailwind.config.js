/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',    // Adjust this path if your templates are in a different folder
    './**/templates/**/*.html', // In case you have app templates inside Django apps
    './static/src/**/*.js',     // Your JS files if you have any with Tailwind classes
  ],
  theme: {
    extend: {
      colors: {
        primary: '#B11226',
        secondary: '#6A1B1A',
        accent: '#D4A017',
        background: '#1A1A1A',
        text: '#F6F1EB',
        border: '#C0C0C0',
      },
    },
  },
  plugins: [],
}
