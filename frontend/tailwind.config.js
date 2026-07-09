/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#1D4ED8",
          hover: "#1E40AF",
        },
        secondary: "#334155",
        success: "#15803D",
        warning: "#B45309",
        danger: "#B91C1C",
        info: "#0369A1",
        surface: {
          DEFAULT: "#FFFFFF",
          muted: "#F1F5F9",
        },
      },
    },
  },
  plugins: [],
};
