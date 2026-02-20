#!/usr/bin/env python3
"""
Script para baixar legendas de vídeos do YouTube.
Uso: python transcribe.py "<URL_DO_VIDEO>" [--lang IDIOMA]
"""

import sys
import json
import re
import time
import argparse

import requests
import yt_dlp


# ── Cache em memória (evita requisições repetidas ao YouTube) ──
_cache = {}
CACHE_TTL = 300  # 5 minutos


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


def _get_ydl_opts():
    """Configurações otimizadas do yt-dlp para evitar rate limiting."""
    return {
        'quiet': True,
        'no_warnings': True,
        # Anti-rate-limiting
        'sleep_interval_requests': 1,       # 1s entre requisições
        'socket_timeout': 30,               # timeout maior
        'retries': 5,                        # mais tentativas
        'fragment_retries': 5,
        'extractor_retries': 3,
        'force_ipv4': True,                  # evita bloqueio IPv6
        # Simula user agent de navegador real
        'http_headers': {
            'User-Agent': (
                'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) '
                'Gecko/20100101 Firefox/128.0'
            ),
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        },
    }


def _try_with_cookies(ydl_opts):
    """Tenta adicionar cookies do Firefox para parecer um usuário logado."""
    try:
        opts_with_cookies = dict(ydl_opts)
        opts_with_cookies['cookiesfrombrowser'] = ('firefox',)
        # Testa se consegue acessar os cookies
        with yt_dlp.YoutubeDL(opts_with_cookies) as ydl:
            pass
        return opts_with_cookies
    except Exception:
        return ydl_opts


def _extract_with_retry(video_url, max_retries=3):
    """Extrai info do vídeo com retry exponential backoff."""
    ydl_opts = _get_ydl_opts()

    for attempt in range(max_retries):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(video_url, download=False)

        except yt_dlp.utils.DownloadError as e:
            error_str = str(e)

            if '429' in error_str or 'Too Many Requests' in error_str:
                if attempt < max_retries - 1:
                    wait = (attempt + 1) * 5  # 5s, 10s, 15s
                    print(f"⏳ Rate limited (429). Aguardando {wait}s... (tentativa {attempt + 2}/{max_retries})")
                    time.sleep(wait)

                    # Na segunda tentativa, tenta com cookies do navegador
                    if attempt == 0:
                        print("🍪 Tentando com cookies do Firefox...")
                        ydl_opts = _try_with_cookies(ydl_opts)
                    continue
                else:
                    raise
            else:
                raise

    raise Exception("Falha após múltiplas tentativas.")


def download_subtitles(video_url, lang=None):
    """
    Tenta baixar legendas existentes do vídeo.
    Prefere legendas manuais; fallback para auto-geradas.
    Retorna (texto, titulo) ou None se não houver legendas.
    """
    # Verifica cache
    cache_key = f"{video_url}:{lang}"
    if cache_key in _cache:
        cached = _cache[cache_key]
        if time.time() - cached['time'] < CACHE_TTL:
            print("⚡ Usando cache...")
            return cached['text'], cached['title']

    print(f"🔍 Verificando legendas disponíveis...")

    info = _extract_with_retry(video_url)

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
    resp = requests.get(escolhido['url'], timeout=15)
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

    if not texto.strip():
        return None, video_title

    result_text = texto.strip()

    # Salva no cache
    _cache[cache_key] = {
        'text': result_text,
        'title': video_title,
        'time': time.time(),
    }

    return result_text, video_title



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
