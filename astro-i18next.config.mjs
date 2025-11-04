import en from "./public/locales/en/translation.json" with { type: "json" };
import ru from "./public/locales/ru/translation.json" with { type: "json" };

/** @type {import('astro-i18next').AstroI18nextConfig} */
export default {
    defaultLocale: "en",
    locales: ["en", "ru"],
    namespaces: ["translation"],
    defaultNamespace: "translation",
    i18nextServer: {
        debug: false,
        initImmediate: false,
        resources: {
            en: {
                translation: en
            },
            ru: {
                translation: ru
            }
        }
    },
    routes: {
        ru: {
            cv: "cv",
        },
    },
};