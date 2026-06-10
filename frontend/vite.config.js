import { defineConfig } from 'vite'
import react, { reactCompilerPreset } from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'

// https://vite.dev/config/
export default defineConfig({
  // Single source of truth: load env from the repo root .env, not frontend/.
  envDir: '..',
  plugins: [react(), babel({ presets: [reactCompilerPreset()] })],
})
