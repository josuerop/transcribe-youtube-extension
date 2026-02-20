# 🎬 YouTube Subtitle Downloader

Ferramenta para baixar legendas de vídeos do YouTube automaticamente. Busca legendas existentes (manuais ou auto-geradas) via yt-dlp e salva o texto em arquivo `.txt`.

Disponível como **CLI** (linha de comando) e como **interface web** via Streamlit.

## ✨ Funcionalidades

- 📄 Download de legendas existentes (manuais e auto-geradas)
- 🌍 Detecção automática de idioma
- 🖥️ Interface web moderna com Streamlit
- 📥 Download direto da transcrição em `.txt`

## 📋 Requisitos

- Python 3.8+

## 🚀 Instalação

```bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/scraping-youtube.git
cd scraping-youtube

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

## 💻 Uso

### Interface Web (Streamlit)

```bash
streamlit run streamlit_app.py
```

Acesse `http://localhost:8501` no navegador, cole a URL do vídeo e clique em **Transcrever**.

### Linha de Comando (CLI)

```bash
# Baixar legendas de um vídeo (idioma detectado automaticamente)
python transcribe.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Especificar idioma das legendas
python transcribe.py "https://www.youtube.com/watch?v=VIDEO_ID" --lang pt
```

A transcrição será salva em um arquivo `.txt` com o título do vídeo.

## ☁️ Deploy no Streamlit Cloud

1. Faça push do repositório para o GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte seu repositório GitHub
4. Selecione `streamlit_app.py` como o arquivo principal
5. Clique em **Deploy** — pronto! 🎉

## 📦 Dependências

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — Extração de metadados e legendas do YouTube
- [requests](https://docs.python-requests.org/) — Requisições HTTP
- [streamlit](https://streamlit.io/) — Interface web interativa

## 📄 Licença

MIT
