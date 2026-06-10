import { defineConfig, loadEnv } from 'vite'
import react, { reactCompilerPreset } from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Single source of truth: load env from the repo root .env, not frontend/.
  const envDir = '..'
  const env = loadEnv(mode, envDir, 'VITE_')
  if (!env.VITE_API_URL) {
    throw new Error('VITE_API_URL is not set in .env')
  }

  return {
    envDir,
    plugins: [react(), babel({ presets: [reactCompilerPreset()] })],
  }
})
