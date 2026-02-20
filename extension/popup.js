/**
 * YouTube Subtitle Downloader — Popup Logic
 * Captura URL da aba ativa, chama a API, e exibe resultado.
 */

// ⚠️ IMPORTANTE: Atualize esta URL após o deploy no Render
const API_URL = "http://localhost:5000";

// ── DOM Elements ──
const notYoutube = document.getElementById("not-youtube");
const mainContent = document.getElementById("main-content");
const videoUrlEl = document.getElementById("video-url");
const langSelect = document.getElementById("lang-select");
const transcribeBtn = document.getElementById("transcribe-btn");
const loadingEl = document.getElementById("loading");
const errorEl = document.getElementById("error");
const errorText = document.getElementById("error-text");
const resultEl = document.getElementById("result");
const resultTitle = document.getElementById("result-title");
const resultText = document.getElementById("result-text");
const wordCount = document.getElementById("word-count");
const charCount = document.getElementById("char-count");
const downloadBtn = document.getElementById("download-btn");
const copyBtn = document.getElementById("copy-btn");

let currentVideoUrl = "";
let currentTranscription = "";
let currentTitle = "";

// ── Init ──
async function init() {
    try {
        const tabs = await browser.tabs.query({ active: true, currentWindow: true });
        const tab = tabs[0];
        const url = tab.url || "";

        if (url.includes("youtube.com/watch") || url.includes("youtu.be/")) {
            currentVideoUrl = url;
            videoUrlEl.textContent = url.length > 60 ? url.substring(0, 60) + "..." : url;
            mainContent.style.display = "block";
        } else {
            notYoutube.style.display = "block";
        }
    } catch (err) {
        notYoutube.style.display = "block";
    }
}

// ── Show/Hide States ──
function showLoading() {
    mainContent.style.display = "none";
    errorEl.style.display = "none";
    resultEl.style.display = "none";
    loadingEl.style.display = "block";
}

function showError(msg) {
    loadingEl.style.display = "none";
    errorEl.style.display = "block";
    errorText.textContent = msg;
    // Show controls again after error
    mainContent.style.display = "block";
}

function showResult(data) {
    loadingEl.style.display = "none";
    mainContent.style.display = "block";
    resultEl.style.display = "block";

    currentTranscription = data.transcription;
    currentTitle = data.title;

    resultTitle.textContent = `✅ ${data.title}`;
    resultText.textContent = data.transcription;
    wordCount.textContent = `📝 ${data.word_count.toLocaleString()} palavras`;
    charCount.textContent = `🔤 ${data.char_count.toLocaleString()} caracteres`;
}

// ── Transcribe ──
async function transcribe() {
    showLoading();

    const lang = langSelect.value || null;
    const body = { url: currentVideoUrl };
    if (lang) body.lang = lang;

    try {
        const response = await fetch(`${API_URL}/transcribe`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.error || "Erro desconhecido.");
            return;
        }

        showResult(data);
    } catch (err) {
        showError("Não foi possível conectar à API. Verifique se ela está online.");
    }
}

// ── Download ──
function downloadTxt() {
    const safeTitle = currentTitle.replace(/[^a-zA-Z0-9 \-_]/g, "").trim();
    const blob = new Blob([currentTranscription], { type: "text/plain" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `${safeTitle}.txt`;
    a.click();

    URL.revokeObjectURL(url);
}

// ── Copy to Clipboard ──
async function copyToClipboard() {
    try {
        await navigator.clipboard.writeText(currentTranscription);
        copyBtn.textContent = "✅ Copiado!";
        copyBtn.classList.add("btn--copied");
        setTimeout(() => {
            copyBtn.textContent = "📋 Copiar texto";
            copyBtn.classList.remove("btn--copied");
        }, 2000);
    } catch {
        // Fallback
        const textarea = document.createElement("textarea");
        textarea.value = currentTranscription;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        textarea.remove();
        copyBtn.textContent = "✅ Copiado!";
        setTimeout(() => { copyBtn.textContent = "📋 Copiar texto"; }, 2000);
    }
}

// ── Event Listeners ──
transcribeBtn.addEventListener("click", transcribe);
downloadBtn.addEventListener("click", downloadTxt);
copyBtn.addEventListener("click", copyToClipboard);

// ── Start ──
init();
