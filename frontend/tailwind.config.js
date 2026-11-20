/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1890ff',
          light: '#40a9ff',
          dark: '#096dd9',
        },
        background: {
          light: '#e6f7ff',
          white: '#ffffff',
          dark: '#f0f5ff',
        },
        border: {
          DEFAULT: '#bae7ff',
          light: '#e6f7ff',
        },
      },
    },
  },
  plugins: [],
  corePlugins: {
    preflight: false,
  },
}
