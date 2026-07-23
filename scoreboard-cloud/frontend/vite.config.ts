import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Built output is served by Scoreboard.Api under /app/ — the API and the
// leaderboard share one origin in production, so no CORS anywhere.
// `emptyOutDir` only wipes wwwroot/app (never wwwroot/classic).
export default defineConfig({
  plugins: [react()],
  base: '/app/',
  build: {
    outDir: '../Scoreboard.Api/wwwroot/app',
    emptyOutDir: true,
  },
  // Dev loop: `dotnet run` serves the API on 5080, vite proxies to it.
  server: {
    proxy: {
      '/scores': 'http://localhost:5080',
      '/result': 'http://localhost:5080',
    },
  },
})
