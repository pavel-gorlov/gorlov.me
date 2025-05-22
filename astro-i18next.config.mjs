/** @type {import('astro-i18next').AstroI18nextConfig} */
export default {
    defaultLocale: "en",
    locales: ["en", "ru"],
    i18nextServer: {
        debug: true,
        routes: {
            prefixDefaultLocale: false,
        }
    }
};