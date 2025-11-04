(() => {
  // Configuration
  const RUSSIAN_LANGUAGE_CODES = ['ru', 'ru-RU', 'ru-UA', 'ru-BY', 'ru-KZ', 'ru-MD'];
  const CLOUDFLARE_TRACE_URL = 'https://www.cloudflare.com/cdn-cgi/trace';
  const GEO_IP_TIMEOUT = 1000; // 1 second timeout for GeoIP request

  // Check if we're already on the correct language version
  const currentPath = window.location.pathname;
  const isRussianVersion = currentPath.startsWith('/ru');
  const isEnglishVersion = !isRussianVersion;

  // Check for user's manual language choice
  const userChoice = localStorage.getItem('userLanguageChoice');
  if (userChoice === 'manual-en' || userChoice === 'manual-ru') {
    // User has manually selected a language, respect their choice
    return;
  }

  // Function to detect browser language
  function isBrowserLanguageRussian() {
    // Check primary language
    const primaryLang = navigator.language || navigator.userLanguage;
    if (primaryLang && RUSSIAN_LANGUAGE_CODES.some(code => primaryLang.startsWith(code))) {
      return true;
    }

    // Check all preferred languages
    if (navigator.languages && navigator.languages.length > 0) {
      return navigator.languages.some(lang =>
        RUSSIAN_LANGUAGE_CODES.some(code => lang.startsWith(code))
      );
    }

    return false;
  }

  // Function to detect country via GeoIP
  async function isUserInRussia() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), GEO_IP_TIMEOUT);

      const response = await fetch(CLOUDFLARE_TRACE_URL, {
        signal: controller.signal,
        cache: 'no-cache'
      });
      clearTimeout(timeoutId);

      if (!response.ok) {
        return false;
      }

      const text = await response.text();
      // Parse the response to get country code
      // Format: loc=XX where XX is the country code
      const match = text.match(/loc=([A-Z]{2})/);
      const countryCode = match ? match[1] : null;

      // Check for Russia and neighboring Russian-speaking countries
      return countryCode === 'RU' || countryCode === 'BY' || countryCode === 'KZ';
    } catch (error) {
      // If GeoIP detection fails, fallback to language detection only
      return false;
    }
  }

  // Function to perform redirect
  function redirectToRussianVersion() {
    // Don't redirect if already on Russian version
    if (isRussianVersion) return;

    // Build the Russian URL
    let newPath = '/ru' + currentPath;

    // Handle special case for home page
    if (currentPath === '/') {
      newPath = '/ru/';
    }

    // Also preserve query string and hash if present
    const queryString = window.location.search;
    const hash = window.location.hash;
    const fullUrl = newPath + queryString + hash;

    // Mark this as an automatic redirect (not manual choice)
    localStorage.setItem('autoRedirected', 'true');

    // Perform redirect
    window.location.href = fullUrl;
  }

  // Function to perform redirect to English version
  function redirectToEnglishVersion() {
    // Don't redirect if already on English version
    if (isEnglishVersion) return;

    // Remove /ru prefix
    let newPath = currentPath.replace(/^\/ru/, '') || '/';

    // Preserve query string and hash
    const queryString = window.location.search;
    const hash = window.location.hash;
    const fullUrl = newPath + queryString + hash;

    // Mark this as an automatic redirect
    localStorage.setItem('autoRedirected', 'true');

    // Perform redirect
    window.location.href = fullUrl;
  }

  // Main detection logic
  async function detectAndRedirect() {
    // Check if we've already auto-redirected in this session
    // This prevents redirect loops
    const hasAutoRedirected = sessionStorage.getItem('hasAutoRedirected');
    if (hasAutoRedirected === 'true') {
      return;
    }

    // Check browser language
    const isRussianBrowser = isBrowserLanguageRussian();

    // Check GeoIP (with timeout)
    const isInRussia = await isUserInRussia();

    // Decide whether to redirect
    const shouldUseRussian = isRussianBrowser || isInRussia;

    if (shouldUseRussian && isEnglishVersion) {
      // Mark that we've done an auto-redirect this session
      sessionStorage.setItem('hasAutoRedirected', 'true');
      redirectToRussianVersion();
    } else if (!shouldUseRussian && isRussianVersion) {
      // If user is not Russian and on Russian version, consider redirecting to English
      // But only if they haven't explicitly chosen Russian
      const autoRedirected = localStorage.getItem('autoRedirected');
      if (autoRedirected === 'true') {
        // They were auto-redirected to Russian but shouldn't be there
        sessionStorage.setItem('hasAutoRedirected', 'true');
        redirectToEnglishVersion();
      }
    }
  }

  // Run detection
  detectAndRedirect();
})();