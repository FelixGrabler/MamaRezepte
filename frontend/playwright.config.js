import { defineConfig } from '@playwright/test'
export default defineConfig({
  testDir: './tests',
  workers: 1,
  use: { baseURL: 'http://localhost:15173', headless: true },
  webServer: [
    { command: `${process.env.PYTHON_BIN || '../.venv/bin/python'} ../backend/tests/browser_server.py`, url: 'http://127.0.0.1:18051/health', reuseExistingServer: false },
    { command: 'npm run dev -- --port 15173 --strictPort', url: 'http://localhost:15173', env: { VITE_PROXY_TARGET: 'http://127.0.0.1:18051' }, reuseExistingServer: false }
  ]
})
