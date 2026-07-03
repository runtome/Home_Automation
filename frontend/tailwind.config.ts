import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        online: "#22c55e",
        offline: "#9ca3af",
      },
    },
  },
  plugins: [],
};

export default config;
