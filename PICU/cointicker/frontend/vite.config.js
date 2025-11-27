/**
 * ⚠️ 주의: 삭제 및 수정 금지 ⚠️
 *
 * 이 파일은 GUI와 백엔드 포트 동기화와 연동되어 있습니다:
 * - server.port: run_dev.sh에서 설정한 PORT/VITE_PORT 환경 변수 사용
 * - server.proxy['/api'].target: run_dev.sh에서 설정한 VITE_API_BASE_URL 사용
 * - 백엔드 포트가 변경되면 run_dev.sh가 자동으로 VITE_API_BASE_URL 업데이트
 *
 * 연동된 컴포넌트:
 * - frontend/run_dev.sh: PORT, VITE_PORT, VITE_API_BASE_URL 환경 변수 설정
 * - backend/run_server.sh: 백엔드 포트 파일 생성 (config/.backend_port)
 * - frontend/src/services/api.js: API 기본 URL 사용
 *
 * 이 파일의 proxy 설정을 수정하면 프론트엔드와 백엔드 포트 동기화가 깨집니다.
 */

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: parseInt(process.env.PORT || process.env.VITE_PORT || "3000", 10),
    proxy: {
      "/api": {
        target:
          process.env.VITE_API_BASE_URL ||
          `http://localhost:${process.env.BACKEND_PORT || "5000"}`,
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, "index.html"),
        // 정적 HTML 파일들도 빌드에 포함 (선택적)
        // architecture: resolve(__dirname, 'public/architecture.html'),
        // performance: resolve(__dirname, 'public/performance.html'),
      },
    },
  },
  // public 폴더의 정적 파일 서빙
  publicDir: "public",
});
