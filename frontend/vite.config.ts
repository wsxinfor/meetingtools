import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import { fileURLToPath, URL } from 'node:url'
import fs from 'node:fs'
import path from 'node:path'

const certsDir = path.resolve(__dirname, 'certs')
const hasCerts =
  fs.existsSync(path.join(certsDir, 'dev.key')) &&
  fs.existsSync(path.join(certsDir, 'dev.crt'))

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({ resolvers: [ElementPlusResolver()] }),
    Components({ resolvers: [ElementPlusResolver()] }),
  ],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    https: hasCerts
      ? {
          key: fs.readFileSync(path.join(certsDir, 'dev.key')),
          cert: fs.readFileSync(path.join(certsDir, 'dev.crt')),
        }
      : true,
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        proxyTimeout: 7200000,
        timeout: 7200000,
      },
    },
  },
})
