#!/usr/bin/env python3
"""
🎬 YouTube Subtitle Downloader — Flask API
Endpoint REST para baixar legendas de vídeos do YouTube.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from transcribe import download_subtitles

app = Flask(__name__)
CORS(app)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


@app.route("/transcribe", methods=["POST"])
def transcribe():
    """
    Recebe URL do YouTube e retorna a transcrição.
    Body: {"url": "https://youtube.com/watch?v=...", "lang": "pt"}
    """
    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({"error": "Campo 'url' é obrigatório."}), 400

    video_url = data["url"]
    lang = data.get("lang")

    # Validação básica
    if "youtube.com" not in video_url and "youtu.be" not in video_url:
        return jsonify({"error": "URL inválida. Use um link do YouTube."}), 400

    try:
        transcription, video_title = download_subtitles(video_url, lang)

        if not transcription:
            return jsonify({"error": "Nenhuma legenda disponível para este vídeo."}), 404

        return jsonify({
            "title": video_title,
            "transcription": transcription,
            "word_count": len(transcription.split()),
            "char_count": len(transcription),
        })

    except Exception as e:
        error_msg = str(e)
        if "is not a valid URL" in error_msg or "Unsupported URL" in error_msg:
            return jsonify({"error": "URL inválida."}), 400
        elif "Video unavailable" in error_msg:
            return jsonify({"error": "Vídeo indisponível ou privado."}), 404
        else:
            return jsonify({"error": f"Erro: {error_msg}"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
