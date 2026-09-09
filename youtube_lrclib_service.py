"""
YouTube Downloader & LRCLIB Synchronized Lyrics Service
Handles YouTube audio extraction via yt-dlp and LRCLIB API queries.
"""

import os
import re
import json
import ssl
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, Optional
import certifi
import yt_dlp

# Fix macOS Python SSL certificate verification
try:
    CA_FILE = certifi.where()
    os.environ["SSL_CERT_FILE"] = CA_FILE
    os.environ["REQUESTS_CA_BUNDLE"] = CA_FILE
except Exception:
    CA_FILE = None

try:
    ssl_context = ssl.create_default_context(cafile=CA_FILE) if CA_FILE else ssl._create_unverified_context()
except Exception:
    ssl_context = ssl._create_unverified_context()

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

NODE_PATH = "/usr/local/bin/node" if os.path.exists("/usr/local/bin/node") else None

LRCLIB_BASE_URL = "https://lrclib.net"
USER_AGENT = "HuayuKaraoke/1.0 (https://github.com/mandarin-karaoke)"


def extract_youtube_id(url: str) -> Optional[str]:
    """Extracts 11-character YouTube video ID from various URL formats."""
    if not url:
        return None
    patterns = [
        r'(?:v=|\/v\/|youtu\.be\/|\/embed\/|\/shorts\/)([a-zA-Z0-9_-]{11})',
        r'^[a-zA-Z0-9_-]{11}$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url.strip())
        if match:
            return match.group(1) if match.groups() else match.group(0)
    return None


def get_youtube_video_info(url: str) -> Dict[str, Any]:
    """
    Retrieves video title, author, and description using oEmbed API
    or yt-dlp metadata extraction without downloading.
    """
    clean_url = url.strip()
    # Attempt 1: Fast oEmbed API query
    try:
        oembed_url = f"https://www.youtube.com/oembed?url={urllib.parse.quote(clean_url)}&format=json"
        req = urllib.request.Request(oembed_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=6, context=ssl_context) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {
                "title": data.get("title", ""),
                "author": data.get("author_name", ""),
                "thumbnail": data.get("thumbnail_url", "")
            }
    except Exception:
        pass

    # Attempt 2: yt-dlp metadata extraction
    try:
        ydl_opts = {
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "nocheckcertificate": True,
        }
        if CA_FILE:
            ydl_opts["cafile"] = CA_FILE
        if NODE_PATH:
            ydl_opts["js_runtimes"] = {"node": {"path": NODE_PATH}}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            return {
                "title": info.get("title", ""),
                "author": info.get("uploader", "") or info.get("channel", ""),
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail", "")
            }
    except Exception as e:
        print(f"yt-dlp extract info error: {e}")
        return {
            "title": "YouTube Mandarin Song",
            "author": "Mandarin Artist",
            "thumbnail": ""
        }


def download_youtube_audio(youtube_url: str, output_dir: str, song_id: str) -> Dict[str, Any]:
    """
    Downloads audio from YouTube video into output_dir using yt-dlp.
    Prefers native m4a/mp3 streams compatible with HTML5 audio playback.
    """
    os.makedirs(output_dir, exist_ok=True)
    out_template = os.path.join(output_dir, f"{song_id}.%(ext)s")

    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio/best",
        "outtmpl": out_template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
    }
    if CA_FILE:
        ydl_opts["cafile"] = CA_FILE
    if NODE_PATH:
        ydl_opts["js_runtimes"] = {"node": {"path": NODE_PATH}}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url.strip(), download=True)
        title = info.get("title", "Imported YouTube Song")
        uploader = info.get("uploader", "") or info.get("channel", "")
        duration = info.get("duration", 0)

    # Locate the created audio file
    found_file = None
    for f in os.listdir(output_dir):
        if f.startswith(f"{song_id}."):
            found_file = f
            break

    if not found_file:
        raise RuntimeError(f"Could not find downloaded audio for {song_id} in {output_dir}")

    full_path = os.path.join(output_dir, found_file)
    return {
        "filename": found_file,
        "filepath": full_path,
        "title": title,
        "author": uploader,
        "duration": duration
    }


def fetch_lrclib_lyrics(track_name: str, artist_name: str, album_name: Optional[str] = None, duration: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Queries LRCLIB (https://lrclib.net/docs) for synchronized lyrics.
    Tries GET /api/get, with fallback to GET /api/search.
    """
    if not track_name:
        return None

    headers = {"User-Agent": USER_AGENT}

    # Attempt 1: Exact match query (/api/get)
    query_params = {
        "track_name": track_name.strip(),
        "artist_name": artist_name.strip() if artist_name else ""
    }
    if album_name and album_name.strip():
        query_params["album_name"] = album_name.strip()
    if duration and duration > 0:
        query_params["duration"] = int(duration)

    get_url = f"{LRCLIB_BASE_URL}/api/get?{urllib.parse.urlencode(query_params)}"
    try:
        req = urllib.request.Request(get_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("syncedLyrics") or data.get("plainLyrics"):
                return data
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"LRCLIB /api/get HTTP error {e.code}: {e}")
    except Exception as e:
        print(f"LRCLIB /api/get error: {e}")

    # Attempt 2: Search query (/api/search)
    search_q = f"{track_name} {artist_name}".strip()
    search_url = f"{LRCLIB_BASE_URL}/api/search?q={urllib.parse.quote(search_q)}"
    try:
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as resp:
            results = json.loads(resp.read().decode("utf-8"))
            if isinstance(results, list) and results:
                # Prioritize entries with syncedLyrics
                for item in results:
                    if item.get("syncedLyrics"):
                        return item
                return results[0]
    except Exception as e:
        print(f"LRCLIB /api/search error: {e}")

    return None

