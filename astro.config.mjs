// @ts-check
import { defineConfig } from 'astro/config';
import astroI18next from "astro-i18next";
import tailwindcss from "@tailwindcss/vite";

// https://astro.build/config
export default defineConfig({
    i18n: {
        defaultLocale: "en",
        locales: ["en", "ru"],
        routing: {
            prefixDefaultLocale: false
        }
    },
    integrations: [astroI18next()],
    vite: {
        plugins: [tailwindcss()],
    },
});