/**
 * YouTube Subtitle Downloader — Firefox Extension
 * Captura a URL do vídeo do YouTube na aba ativa e abre o app Streamlit.
 */

const STREAMLIT_APP_URL = "https://transcribe-youtube-extension-vacd4x7eansewwmvdapprnc.streamlit.app/";

browser.browserAction.onClicked.addListener((tab) => {
    const url = tab.url || "";

    // Verifica se a aba atual é um vídeo do YouTube
    if (url.includes("youtube.com/watch") || url.includes("youtu.be/")) {
        // Codifica a URL do vídeo e redireciona para o app Streamlit
        const encodedUrl = encodeURIComponent(url);
        const appUrl = `${STREAMLIT_APP_URL}?video_url=${encodedUrl}`;
        browser.tabs.create({ url: appUrl });
    } else {
        // Se não estiver no YouTube, abre o app sem URL
        browser.tabs.create({ url: STREAMLIT_APP_URL });
    }
});
