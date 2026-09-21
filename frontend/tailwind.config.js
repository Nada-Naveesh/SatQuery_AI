/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        void: {
          950: '#070709',
          900: '#0d0d12',
          850: '#121218',
          800: '#181822',
          700: '#232332',
          600: '#323246',
        },
        crimson: {
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
          950: '#450a0a',
        },
        space: {
          950: '#070709',
          900: '#0d0d12',
          850: '#121218',
          800: '#181822',
          700: '#232332',
          600: '#323246',
        },
        isro: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626',
          900: '#7f1d1d',
        }
      },
    },
  },
  plugins: [],
};
