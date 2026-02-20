# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YouTube subtitle downloader. Fetches existing captions (manual or auto-generated) from YouTube videos via yt-dlp. Available as a CLI tool, a Streamlit web UI, and a Firefox browser extension.

## Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# CLI — Run (requires a YouTube URL as argument; quote URLs containing &)
python transcribe.py "<YOUTUBE_URL>"

# CLI — Force a specific subtitle language (e.g. Portuguese, English, Spanish)
python transcribe.py "<YOUTUBE_URL>" --lang pt

# Web UI — Start the Streamlit app (access at http://localhost:8501)
streamlit run streamlit_app.py
```

## Architecture

Three components share the same core subtitle-fetching logic:

### `transcribe.py` — Core CLI script

`download_subtitles()` fetches existing captions via yt-dlp metadata (no audio download). Prefers manual captions over auto-generated; prefers the requested/detected language, then falls back to English. Format preference: `json3` → `vtt`. `json3_to_text()` converts the YouTube json3 format to plain text; VTT is parsed with regex to strip timestamps and deduplicate lines.

Ends with `save_transcription()`, which sanitizes the video title (alphanumeric + space/dash/underscore) and writes `<title>.txt` in the current directory.

### `streamlit_app.py` — Web UI

Streamlit app that imports `download_subtitles()` from `transcribe.py`. Accepts a YouTube URL via text input or via `?video_url=` query parameter (used by the Firefox extension). Provides in-browser preview with word/character stats and a download button for the `.txt` file.

### `extension/` — Firefox browser extension (Manifest v2)

Captures the current YouTube tab URL and opens the deployed Streamlit app with `?video_url=` query param. The Streamlit deployment URL is hardcoded in `background.js`. Uses `browser_action` with `activeTab` permission — no popup, just a single-click icon.

## Configuration

- `.streamlit/config.toml` — Purple dark theme and headless server mode.

## Dependencies

- **yt-dlp**: YouTube metadata extraction and subtitle download
- **requests**: HTTP download of subtitle files
- **streamlit**: Web UI framework

## Language

Code comments and UI strings are in Brazilian Portuguese.
