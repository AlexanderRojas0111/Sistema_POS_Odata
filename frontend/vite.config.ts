import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Configuración Enterprise para Sistema Sabrositas POS
export default defineConfig({
  plugins: [react()],
  
  // Configuración del servidor de desarrollo
  server: {
    port: 5173,
    host: '0.0.0.0',
    strictPort: true,
    open: false, // No abrir automáticamente
    cors: true,
    
    // Configuración HMR robusta
    hmr: {
      port: 5173,
      host: 'localhost',
      clientPort: 5173,
      overlay: true
    },
    
    // Proxy para APIs - Compatible con MySQL backend
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        ws: true, // WebSocket support
        rewrite: (path) => path,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('Proxy error:', err);
          });
          proxy.on('proxyReq', (_proxyReq, req, _res) => {
            console.log('Sending Request to the Target:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
          });
        }
      }
    }
  },
  
  // Configuración de build para producción
  build: {
    outDir: 'dist',
    sourcemap: process.env.NODE_ENV === 'development',
    minify: 'terser',
    target: 'es2020',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          ui: ['lucide-react', 'framer-motion'],
          forms: ['react-hook-form'],
          http: ['axios']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },
  
  // Configuración de preview para testing
  preview: {
    port: 4173,
    host: '0.0.0.0',
    strictPort: true
  },
  
  // Variables de entorno
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '2.0.0'),
    __API_URL__: JSON.stringify(process.env.VITE_API_URL || 'http://localhost:8000')
  },
  
  // Optimizaciones
  optimizeDeps: {
    include: ['react', 'react-dom', 'axios', 'react-router-dom']
  },
  
  // Configuración de CSS
  css: {
    devSourcemap: true,
    preprocessorOptions: {
      scss: {
        additionalData: `@import "./src/styles/variables.scss";`
      }
    }
  }
})
