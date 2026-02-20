#!/usr/bin/env python3
"""
🎬 YouTube Subtitle Downloader — Streamlit Web Interface
Interface visual para baixar legendas de vídeos do YouTube.
"""

import streamlit as st
from transcribe import download_subtitles


# ─── Page Configuration ───────────────────────────────────────────────
st.set_page_config(
    page_title="YouTube Subtitle Downloader",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Import Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global ── */
    *, .stApp {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(160deg, #0f0c29 0%, #1a1245 35%, #24243e 100%);
    }

    /* ── Header ── */
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem;
    }

    .main-header h1 {
        background: linear-gradient(135deg, #a78bfa, #7c3aed, #6d28d9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0.3rem;
    }

    .main-header p {
        color: #a5b4fc;
        font-size: 1.1rem;
        font-weight: 300;
        opacity: 0.85;
    }

    /* ── Glass Card ── */
    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    .glass-card:hover {
        border-color: rgba(167, 139, 250, 0.25);
        box-shadow: 0 8px 40px rgba(124, 58, 237, 0.15);
    }

    /* ── Input styling ── */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        font-size: 1rem !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #7c3aed !important;
        box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2) !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #6b7280 !important;
    }

    /* ── Selectbox ── */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
    }

    /* ── Primary Button ── */
    .stButton > button[kind="primary"],
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.3px !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.35) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(124, 58, 237, 0.5) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ── Download Button ── */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #059669, #047857) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(5, 150, 105, 0.35) !important;
    }

    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(5, 150, 105, 0.5) !important;
    }

    /* ── Result text area ── */
    .result-area {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        color: #cbd5e1;
        font-size: 0.95rem;
        line-height: 1.7;
        max-height: 400px;
        overflow-y: auto;
        margin: 1rem 0;
    }

    /* ── Stats badges ── */
    .stats-row {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
        flex-wrap: wrap;
    }

    .stat-badge {
        background: rgba(124, 58, 237, 0.15);
        border: 1px solid rgba(124, 58, 237, 0.25);
        border-radius: 10px;
        padding: 0.5rem 1rem;
        color: #c4b5fd;
        font-size: 0.85rem;
        font-weight: 500;
        flex: 1;
        text-align: center;
        min-width: 120px;
    }

    /* ── Alert styling ── */
    .stAlert {
        border-radius: 12px !important;
    }

    /* ── Spinner ── */
    .stSpinner > div {
        border-top-color: #7c3aed !important;
    }

    /* ── Footer ── */
    .footer {
        text-align: center;
        color: #4b5563;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-bottom: 2rem;
    }

    .footer a {
        color: #7c3aed;
        text-decoration: none;
    }

    /* ── Hide default streamlit elements ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ── Divider ── */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(124, 58, 237, 0.3), transparent);
        margin: 1.5rem 0;
        border: none;
    }
</style>
""", unsafe_allow_html=True)


# ─── Header ───────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🎬 YouTube Subtitle Downloader</h1>
    <p>Extraia legendas de qualquer vídeo do YouTube em segundos</p>
</div>
""", unsafe_allow_html=True)


# ─── Input Section ────────────────────────────────────────────────────
video_url = st.text_input(
    "🔗 URL do Vídeo",
    placeholder="https://www.youtube.com/watch?v=...",
    help="Cole a URL completa do vídeo do YouTube",
)

col1, col2 = st.columns([1, 1])

with col1:
    lang_options = {
        "🌍 Auto-detectar": None,
        "🇧🇷 Português": "pt",
        "🇺🇸 English": "en",
        "🇪🇸 Español": "es",
        "🇫🇷 Français": "fr",
        "🇩🇪 Deutsch": "de",
        "🇯🇵 日本語": "ja",
        "🇰🇷 한국어": "ko",
    }
    selected_lang = st.selectbox(
        "🌐 Idioma das legendas",
        options=list(lang_options.keys()),
        index=0,
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    transcribe_btn = st.button("🚀 Transcrever", type="primary", use_container_width=True)


# ─── Processing ───────────────────────────────────────────────────────
if transcribe_btn:
    if not video_url or not video_url.strip():
        st.error("⚠️ Por favor, insira a URL de um vídeo do YouTube.")
    elif "youtube.com" not in video_url and "youtu.be" not in video_url:
        st.error("⚠️ URL inválida. Insira um link válido do YouTube.")
    else:
        lang = lang_options[selected_lang]

        with st.spinner("🔍 Buscando legendas... Isso pode levar alguns segundos."):
            try:
                transcription, video_title = download_subtitles(video_url, lang)

                if not transcription:
                    st.warning("😕 Nenhuma legenda disponível para este vídeo.")
                else:
                    # Store results in session state
                    st.session_state["transcription"] = transcription
                    st.session_state["video_title"] = video_title

            except Exception as e:
                error_msg = str(e)
                if "is not a valid URL" in error_msg or "Unsupported URL" in error_msg:
                    st.error("❌ URL inválida. Verifique o link e tente novamente.")
                elif "Video unavailable" in error_msg:
                    st.error("❌ Vídeo indisponível. Ele pode ser privado ou ter sido removido.")
                else:
                    st.error(f"❌ Erro ao processar o vídeo: {error_msg}")


# ─── Results Section ──────────────────────────────────────────────────
if "transcription" in st.session_state and st.session_state["transcription"]:
    transcription = st.session_state["transcription"]
    video_title = st.session_state["video_title"]

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    st.markdown(f"### ✅ Transcrição: *{video_title}*")

    # Stats
    word_count = len(transcription.split())
    char_count = len(transcription)
    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-badge">📝 {word_count:,} palavras</div>
        <div class="stat-badge">🔤 {char_count:,} caracteres</div>
    </div>
    """, unsafe_allow_html=True)

    # Text display
    st.markdown(f'<div class="result-area">{transcription}</div>', unsafe_allow_html=True)

    # Download button
    safe_title = "".join(
        c for c in video_title if c.isalnum() or c in (' ', '-', '_')
    ).rstrip()

    st.download_button(
        label="📥 Baixar Transcrição (.txt)",
        data=transcription,
        file_name=f"{safe_title}.txt",
        mime="text/plain",
        use_container_width=True,
    )


# ─── Footer ───────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <div class="custom-divider"></div>
    Feito com ❤️ usando <a href="https://streamlit.io" target="_blank">Streamlit</a>
    &nbsp;•&nbsp; Powered by <a href="https://github.com/yt-dlp/yt-dlp" target="_blank">yt-dlp</a>
</div>
""", unsafe_allow_html=True)
