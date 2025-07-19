import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import { VitePluginFonts } from 'vite-plugin-fonts'


export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    VitePluginFonts({
      google: {
        families: [
          {
            name: 'Inter'
          },
          {
            name: 'Roboto'
          }
        ]
      }
    }),
  ],
  build: {
  },
  optimizeDeps: {
  },
})
