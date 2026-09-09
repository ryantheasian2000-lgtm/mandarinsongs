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
    Uses multi-strategy candidate extraction (exact GET /api/get, Chinese token matching,
    and /api/search with duration scoring) to reliably resolve lyrics from YouTube titles.
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
    def _extract_chinese(text: str) -> str:
        return "".join(re.findall(r"[\u4e00-\u9fff]+", text or ""))

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
    def _clean_title(text: str) -> str:
        cleaned = text or ""
        for tag in [
            "【Official MV】", "[Official MV]", "【官方MV】", "官方MV", "Official Music Video",
            "Official Video", "Official Audio", "MV", "HD", "4K", "1080P", "1080p",
            "（歌詞版）", "【歌詞】", "歌詞", "Lyrics", "字幕版", "動態歌詞", "KTV", "Audio", "HQ"
        ]:
            cleaned = re.sub(re.escape(tag), "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip(" -_")

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
    cleaned_track = _clean_title(track_name)
    cleaned_artist = _clean_title(artist_name)

    return None
    # Build prioritized list of (track, artist) candidates for exact /api/get
    get_candidates = []
    if cleaned_track:
        get_candidates.append((cleaned_track, cleaned_artist))

    # Bracket extraction: Artist【Title】or Title【Artist】
    bracket_m = re.search(r"[【《\[\(](.*?)(?:[】》\]\)]|$)", cleaned_track)
    if bracket_m:
        inside = bracket_m.group(1).strip()
        outside = re.sub(r"[【《\[\(].*?(?:[】》\]\)]|$)", " ", cleaned_track).strip(" -_")
        inside_zh = _extract_chinese(inside)
        outside_zh = _extract_chinese(outside)
        if inside_zh and outside_zh:
            get_candidates.append((inside_zh, outside_zh))
            get_candidates.append((outside_zh, inside_zh))
        elif inside_zh:
            get_candidates.append((inside_zh, outside_zh or cleaned_artist))
        elif outside_zh:
            get_candidates.append((outside_zh, inside_zh or cleaned_artist))
        if inside and outside:
            get_candidates.append((inside, outside))

    # Dash split extraction: Artist - Track or Track - Artist
    if " - " in cleaned_track or "-" in cleaned_track:
        parts = [p.strip() for p in re.split(r"\s*-\s*", cleaned_track) if p.strip()]
        if len(parts) >= 2:
            p0, p1 = parts[0], parts[1]
            p0_zh = _extract_chinese(p0)
            p1_zh = _extract_chinese(p1)
            if p0_zh and p1_zh:
                get_candidates.append((p1_zh, p0_zh))
                get_candidates.append((p0_zh, p1_zh))
            get_candidates.append((p1, p0))
            get_candidates.append((p0, p1))

    # Pure Chinese extraction
    track_zh = _extract_chinese(cleaned_track)
    artist_zh = _extract_chinese(cleaned_artist)
    if track_zh and artist_zh:
        get_candidates.append((track_zh, artist_zh))

    # Strategy 1: Attempt exact GET /api/get with each candidate
    tried_get = set()
    for cand_track, cand_artist in get_candidates:
        cand_track = cand_track.strip()
        cand_artist = cand_artist.strip()
        if not cand_track or (cand_track, cand_artist) in tried_get:
            continue
        tried_get.add((cand_track, cand_artist))

        query_params = {
            "track_name": cand_track,
            "artist_name": cand_artist
        }
        if album_name and album_name.strip():
            query_params["album_name"] = album_name.strip()
        if duration and duration > 0:
            query_params["duration"] = int(duration)

        get_url = f"{LRCLIB_BASE_URL}/api/get?{urllib.parse.urlencode(query_params)}"
        try:
            req = urllib.request.Request(get_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8, context=ssl_context) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("syncedLyrics"):
                    return data
                elif data.get("plainLyrics") and not data.get("syncedLyrics"):
                    # Keep as fallback if no synced lyrics found later
                    fallback_plain = data
        except urllib.error.HTTPError as e:
            if e.code != 404:
                print(f"LRCLIB /api/get HTTP {e.code} for ({cand_track}, {cand_artist}): {e}")
        except Exception as e:
            print(f"LRCLIB /api/get error for ({cand_track}, {cand_artist}): {e}")

    # Strategy 2: Attempt search queries via GET /api/search?q=...
    search_queries = []
    # If Chinese track and artist available:
    for cand_track, cand_artist in get_candidates:
        if cand_track and cand_artist:
            search_queries.append(f"{cand_track} {cand_artist}".strip())
    # Track alone (critical when artist is an uploader/label like Pandarin or Rock Records)
    if track_zh:
        search_queries.append(track_zh)
    if cleaned_track:
        search_queries.append(cleaned_track)
    if cleaned_track and cleaned_artist:
        search_queries.append(f"{cleaned_track} {cleaned_artist}".strip())

    best_match = None
    best_score = -1
    tried_search = set()

    for q in search_queries:
        q = q.strip()
        if not q or q in tried_search:
            continue
        tried_search.add(q)

        search_url = f"{LRCLIB_BASE_URL}/api/search?q={urllib.parse.quote(q)}"
        try:
            req = urllib.request.Request(search_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8, context=ssl_context) as resp:
                results = json.loads(resp.read().decode("utf-8"))
                if isinstance(results, list) and results:
                    for item in results:
                        score = 0
                        has_synced = bool(item.get("syncedLyrics"))
                        if has_synced:
                            score += 100
                        elif item.get("plainLyrics"):
                            score += 20

                        # Duration scoring if duration is known
                        item_dur = item.get("duration")
                        if duration and item_dur:
                            diff = abs(int(item_dur) - int(duration))
                            if diff <= 5:
                                score += 50
                            elif diff <= 15:
                                score += 25
                            elif diff <= 30:
                                score += 10

                        # Chinese name matching
                        r_track_zh = _extract_chinese(item.get("trackName", ""))
                        r_artist_zh = _extract_chinese(item.get("artistName", ""))
                        if track_zh and r_track_zh and (track_zh in r_track_zh or r_track_zh in track_zh):
                            score += 30
                        if artist_zh and r_artist_zh and (artist_zh in r_artist_zh or r_artist_zh in artist_zh):
                            score += 20

                        if score > best_score:
                            best_score = score
                            best_match = item

                        # If perfect match found (synced lyrics and high score), return immediately
                        if has_synced and score >= 150:
                            return item
        except Exception as e:
            print(f"LRCLIB /api/search error for {q}: {e}")

    return best_match

