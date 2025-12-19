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

    runtimeConfig: {
        public: {
            apiUrl: process.env.API_URL || 'http://127.0.0.1:8000',
        },
    },
});
