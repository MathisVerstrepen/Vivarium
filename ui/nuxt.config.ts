// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from '@tailwindcss/vite';

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },
  modules: ['@nuxt/eslint', '@nuxt/icon', '@tailwindcss/postcss', 'motion-v/nuxt'],

  css: ['~/assets/css/main.css'],

    vite: {
        plugins: [tailwindcss()],
    },

    typescript: {
        strict: false,
    },
})