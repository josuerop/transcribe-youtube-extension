#!/usr/bin/env python3
"""
Script para baixar legendas de vídeos do YouTube.
Uso: python transcribe.py "<URL_DO_VIDEO>" [--lang IDIOMA]
"""

import re
import sys
import json
import argparse

import requests
import yt_dlp


def json3_to_text(json_content):
    """Converte o formato json3 do YouTube em texto puro."""
    data = json.loads(json_content)
    parts = []

    for event in data.get('events', []):
        segs = event.get('segs', [])
        segment_text = ''.join(seg.get('utf8', '') for seg in segs)
        segment_text = segment_text.replace('\n', ' ').strip()
        if segment_text:
            parts.append(segment_text)

    return ' '.join(parts)


def limpar_texto(texto):
    """Remove artefatos comuns de legendas do YouTube."""
    # Remove colchetes e conteúdo: [Música], [ __ ], [Aplausos], etc.
    texto = re.sub(r'\[[^\]]*\]', '', texto)
    # Remove indicadores de mudança de falante: >>
    texto = re.sub(r'>>', '', texto)
    # Remove símbolos de música: ♪
    texto = re.sub(r'♪', '', texto)
    # Normaliza espaços múltiplos em um só
    texto = re.sub(r' {2,}', ' ', texto)
    return texto.strip()


def download_subtitles(video_url, lang=None):
    """
    Tenta baixar legendas existentes do vídeo.
    Prefere legendas manuais; fallback para auto-geradas.
    Retorna (texto, titulo) ou None se não houver legendas.
    """
    print(f"🔍 Verificando legendas disponíveis...")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {'youtube': {'skip': ['dash', 'hls']}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)

    video_title = info.get('title', 'video')

    # Determina o idioma a usar
    if lang is None:
        lang = info.get('language') or 'pt'
        print(f"🌍 Idioma detectado: {lang}")

    manual = info.get('subtitles', {})
    auto = info.get('automatic_captions', {})

    # Prefere manuais, fallback para auto-geradas
    if lang in manual:
        tracks = manual[lang]
        fonte = 'manuais'
    elif lang in auto:
        tracks = auto[lang]
        fonte = 'auto-geradas'
    else:
        # Tenta inglês como segundo fallback
        if 'en' in manual:
            tracks = manual['en']
            fonte = 'manuais (en)'
            lang = 'en'
        elif 'en' in auto:
            tracks = auto['en']
            fonte = 'auto-geradas (en)'
            lang = 'en'
        else:
            print(f"⚠️  Nenhuma legenda encontrada para o idioma '{lang}'")
            return None, video_title

    # Escolhe o melhor formato disponível (json3 > vtt > outros)
    formatos_preferidos = ['json3', 'vtt']
    escolhido = None
    for fmt_pref in formatos_preferidos:
        for fmt in tracks:
            if fmt.get('ext') == fmt_pref and 'url' in fmt:
                escolhido = fmt
                break
        if escolhido:
            break

    if not escolhido:
        escolhido = next((f for f in tracks if 'url' in f), None)

    if not escolhido:
        return None, video_title

    print(f"📄 Baixando legendas {fonte} (formato: {escolhido['ext']})...")
    resp = requests.get(escolhido['url'], timeout=30)
    resp.raise_for_status()
    conteudo = resp.text

    if escolhido['ext'] == 'json3':
        texto = json3_to_text(conteudo)
    else:
        # Fallback para vtt: remove timestamps e tags inline
        linhas = conteudo.splitlines()
        partes = []
        vistas = set()
        for linha in linhas:
            if (linha.startswith('WEBVTT') or linha.startswith('Kind:') or
                    linha.startswith('Language:') or '-->' in linha or
                    linha.strip() == '' or linha.strip().isdigit()):
                continue
            limpa = re.sub(r'<[^>]+>', '', linha).strip()
            if limpa and limpa not in vistas:
                vistas.add(limpa)
                partes.append(limpa)
        texto = ' '.join(partes)

    texto = limpar_texto(texto)
    if not texto:
        return None, video_title

    return texto, video_title



def save_transcription(transcription, video_title):
    """Salva a transcrição em arquivo .txt."""
    # Remove caracteres inválidos do nome do arquivo
    safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    output_file = f"{safe_title}.txt"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(transcription)

    return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Baixa legendas de vídeos do YouTube.'
    )
    parser.add_argument('url', help='URL do vídeo do YouTube (use aspas para URLs com &)')
    parser.add_argument('--lang', help='Idioma das legendas (ex: pt, en, es). Detecta automaticamente se omitido.')
    args = parser.parse_args()

    video_url = args.url
    lang = args.lang

    try:
        transcription, video_title = download_subtitles(video_url, lang)

        if not transcription:
            print(f"❌ Nenhuma legenda disponível para este vídeo.")
            sys.exit(1)

        output_file = save_transcription(transcription, video_title)
        print(f"💾 Legendas salvas em: {output_file}")

    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    sys.exit(0)
