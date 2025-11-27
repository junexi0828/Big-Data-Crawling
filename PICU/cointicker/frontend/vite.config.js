import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        // 정적 HTML 파일들도 빌드에 포함 (선택적)
        // architecture: resolve(__dirname, 'public/architecture.html'),
        // performance: resolve(__dirname, 'public/performance.html'),
      },
    },
  },
  // public 폴더의 정적 파일 서빙
  publicDir: 'public',
})

