# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YouTube subtitle downloader. Fetches existing captions (manual or auto-generated) from YouTube videos via yt-dlp and saves the text to a `.txt` file in the working directory named after the video title.

## Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run (requires a YouTube URL as argument; quote URLs containing &)
python transcribe.py "<YOUTUBE_URL>"

# Force a specific subtitle language (e.g. Portuguese, English, Spanish)
python transcribe.py "<YOUTUBE_URL>" --lang pt
```

## Architecture

Single-file script (`transcribe.py`) with a single pipeline:

`download_subtitles()` fetches existing captions via yt-dlp metadata (no audio download). Prefers manual captions over auto-generated; prefers the requested/detected language, then falls back to English. Format preference: `json3` → `vtt`. `json3_to_text()` converts the YouTube json3 format to plain text; VTT is parsed with regex to strip timestamps and deduplicate lines.

Ends with `save_transcription()`, which sanitizes the video title (alphanumeric + space/dash/underscore) and writes `<title>.txt` in the current directory.

## Dependencies

- **yt-dlp**: YouTube metadata extraction and subtitle download
- **requests**: HTTP download of subtitle files

## Language

Code comments and UI strings are in Brazilian Portuguese.
