// i18next.config.mjs
export default {
    supportedLngs: ['en', 'ru'],
    fallbackLng: 'en',
    i18next: {
        detection: {
            order: ['path'],
            lookupFromPathIndex: 0,
            caches: [],
        },
        routes: {
            // Настройка путей (опционально)
            en: {
                prefixDefault: true, // /en/ или /
            },
            ru: {
                prefixDefault: false, // /ru/
            },
        },
    },
};
