"""
HuayuKaraoke - Mandarin Song-Based Language Learning Server
Flask application handling audio uploads, lyrics synchronization,
Gemini AI processing, and vocabulary management.
"""

import os
import re
import json
import uuid
import ssl
import certifi
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# Fix macOS Python SSL certificate verification
try:
    _ca_file = certifi.where()
    os.environ["SSL_CERT_FILE"] = _ca_file
    os.environ["REQUESTS_CA_BUNDLE"] = _ca_file
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

import dictionary_service
import gemini_service
import youtube_lrclib_service
from sample_data import SAMPLE_SONGS

app = Flask(__name__, static_folder="static", template_folder="templates")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")
if os.path.exists(ENV_FILE):
    try:
        with open(ENV_FILE, "r", encoding="utf-8") as ef:
            for line in ef:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except Exception:
        pass

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DATA_FOLDER = os.path.join(BASE_DIR, "data")
SONGS_FILE = os.path.join(DATA_FOLDER, "songs.json")
VOCAB_FILE = os.path.join(DATA_FOLDER, "vocab.json")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"mp3", "wav", "ogg", "m4a", "aac", "webm"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_custom_songs() -> list:
    if os.path.exists(SONGS_FILE):
        try:
            with open(SONGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_custom_songs(songs: list):
    with open(SONGS_FILE, "w", encoding="utf-8") as f:
        json.dump(songs, f, ensure_ascii=False, indent=2)


def load_saved_vocab() -> list:
    if os.path.exists(VOCAB_FILE):
        try:
            with open(VOCAB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_saved_vocab(vocab: list):
    with open(VOCAB_FILE, "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/api/songs", methods=["GET"])
def get_songs():
    custom_songs = load_custom_songs()
    all_songs = SAMPLE_SONGS + custom_songs
    # Return summary list
    summary = [
        {
            "id": s["id"],
            "title": s["title"],
            "artist": s.get("artist", "Unknown Artist"),
            "difficulty": s.get("difficulty", "General"),
            "lineCount": len(s.get("lines", [])),
            "isCustom": s.get("isCustom", False)
        }
        for s in all_songs
    ]
    return jsonify({"songs": summary})


@app.route("/api/songs/<song_id>", methods=["GET"])
def get_song(song_id):
    custom_songs = load_custom_songs()
    for s in SAMPLE_SONGS + custom_songs:
        if s["id"] == song_id:
            return jsonify(s)
    return jsonify({"error": "Song not found"}), 404


@app.route("/api/songs/<song_id>", methods=["DELETE"])
def delete_song(song_id):
    custom_songs = load_custom_songs()
    target_idx = None
    target_song = None
    for idx, s in enumerate(custom_songs):
        if s["id"] == song_id:
            target_idx = idx
            target_song = s
            break

    if target_idx is None:
        return jsonify({"error": "Song not found or built-in demo song cannot be deleted"}), 404

    # Delete uploaded audio file if present
    audio_path = target_song.get("audioPath")
    if audio_path and os.path.exists(audio_path):
        try:
            os.remove(audio_path)
        except Exception:
            pass

    custom_songs.pop(target_idx)
    save_custom_songs(custom_songs)
    return jsonify({"success": True, "message": "Song deleted successfully", "deletedId": song_id})


@app.route("/api/songs/<song_id>/translate", methods=["POST"])
def translate_song(song_id):
    custom_songs = load_custom_songs()
    target_song = None
    for s in custom_songs:
        if s["id"] == song_id:
            target_song = s
            break

    if not target_song:
        for s in SAMPLE_SONGS:
            if s["id"] == song_id:
                target_song = dict(s)
                custom_songs.append(target_song)
                break

    if not target_song:
        return jsonify({"error": "Song not found"}), 404

    data = request.get_json(silent=True) or {}
    api_key = data.get("apiKey") or request.headers.get("X-Gemini-API-Key")
    model = data.get("model")

    lines = target_song.get("lines", [])
    if not lines:
        return jsonify({"error": "Song has no lyric lines to translate"}), 400

    try:
        updated_lines = gemini_service.translate_lyrics(
            lines=lines,
            title=target_song.get("title", ""),
            artist=target_song.get("artist", ""),
            api_key=api_key,
            model=model
        )
        target_song["lines"] = updated_lines
        save_custom_songs(custom_songs)
        return jsonify({
            "success": True,
            "message": f"Successfully translated {len(updated_lines)} lines with Gemini!",
            "song": target_song
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/upload", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided in request"}), 400
    
    file = request.files["audio"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit(".", 1)[1].lower()
        song_id = f"song-{uuid.uuid4().hex[:8]}"
        saved_filename = f"{song_id}.{ext}"
        saved_path = os.path.join(UPLOAD_FOLDER, saved_filename)
        file.save(saved_path)

        title = request.form.get("title", file.filename.rsplit(".", 1)[0])
        artist = request.form.get("artist", "Mandarin Song")

        new_song = {
            "id": song_id,
            "title": title,
            "artist": artist,
            "audioUrl": f"/uploads/{saved_filename}",
            "audioPath": saved_path,
            "difficulty": "Custom Upload",
            "isCustom": True,
            "lines": []
        }

        custom_songs = load_custom_songs()
        custom_songs.append(new_song)
        save_custom_songs(custom_songs)

        return jsonify(new_song)
    
    return jsonify({"error": "Invalid file type. Please upload MP3, WAV, M4A, or OGG."}), 400


@app.route("/api/process-song", methods=["POST"])
def process_song():
    """Calls Gemini to transcribe and align audio or auto-generate lyrics with Pinyin and translation."""
    data = request.get_json() or {}
    song_id = data.get("songId")
    api_key = data.get("apiKey")
    model = data.get("model", "gemini-2.5-flash")
    title = data.get("title")
    artist = data.get("artist")

    if not song_id:
        return jsonify({"error": "Missing songId"}), 400

    custom_songs = load_custom_songs()
    target_song = None
    for s in custom_songs:
        if s["id"] == song_id:
            target_song = s
            break

    if not target_song:
        return jsonify({"error": "Song not found"}), 404

    audio_path = target_song.get("audioPath")
    if not audio_path or not os.path.exists(audio_path):
        return jsonify({"error": "Audio file not found on server"}), 404

    try:
        gemini_result = gemini_service.process_song_audio(
            audio_path=audio_path,
            title=title or target_song.get("title"),
            artist=artist or target_song.get("artist"),
            api_key=api_key,
            model=model
        )

        if "title" in gemini_result:
            target_song["title"] = gemini_result["title"]
        if "artist" in gemini_result:
            target_song["artist"] = gemini_result["artist"]
        if "difficulty" in gemini_result:
            target_song["difficulty"] = gemini_result["difficulty"]
        if "languageTip" in gemini_result:
            target_song["languageTip"] = gemini_result["languageTip"]

        lines = gemini_result.get("lines", [])
        for idx, line in enumerate(lines):
            line["id"] = idx
            if not line.get("words"):
                line["words"] = dictionary_service.segment_and_annotate_line(
                    line.get("hanzi", ""), line.get("pinyin", "")
                )

        target_song["lines"] = lines
        save_custom_songs(custom_songs)
        return jsonify(target_song)

    except Exception as e:
        err_str = str(e)
        if "403" in err_str or "policy" in err_str.lower():
            return jsonify({
                "error": f"Gemini API policy restriction (403): {err_str}. Tip: Try selecting a different model in Settings, or use 'Paste LRC / Lyrics' mode for instant offline Pinyin & timestamp alignment without needing Gemini!"
            }), 403
        return jsonify({"error": err_str}), 500




def parse_lrc_text_into_lines(lrc_text: str) -> list:
    """Parses standard LRC lyrics or plain text lyrics, connecting with Pinyin, translation, and word tokens."""
    pattern = re.compile(r'\[(\d{2}):(\d{2})(?:[.:](\d{1,3}))?\](.*)')
    raw_lines = []
    plain_text_lines = []

    for line_str in (lrc_text or "").strip().split("\n"):
        clean_str = line_str.strip()
        if not clean_str:
            continue
        match = pattern.match(clean_str)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            millis_str = match.group(3) or "0"
            if len(millis_str) == 2:
                millis = int(millis_str) * 10
            elif len(millis_str) == 3:
                millis = int(millis_str)
            else:
                millis = int(millis_str) * 100
            
            timestamp = minutes * 60 + seconds + (millis / 1000.0)
            text = match.group(4).strip()
            # Ignore standard LRC metadata tags like [ti:Title], [ar:Artist], [al:Album]
            if text and not (text.startswith("ti:") or text.startswith("ar:") or text.startswith("al:") or text.startswith("by:")):
                raw_lines.append((timestamp, text))
        else:
            # Plain Chinese lyric line without timestamps
            plain_text_lines.append(clean_str)

    parsed_lines = []

    if raw_lines:
        raw_lines.sort(key=lambda x: x[0])
        for i, (ts, text) in enumerate(raw_lines):
            next_ts = raw_lines[i + 1][0] if i + 1 < len(raw_lines) else ts + 4.0
            words = dictionary_service.segment_and_annotate_line(text)
            pinyin_assembled = " ".join(w.get("pinyin", "") for w in words if not w.get("isPunctuation", False))
            
            parsed_lines.append({
                "id": i,
                "startTime": round(ts, 2),
                "endTime": round(next_ts, 2),
                "hanzi": text,
                "pinyin": pinyin_assembled,
                "english": "Click line or word for English definitions",
                "words": words
            })
    elif plain_text_lines:
        current_time = 3.0
        for i, text in enumerate(plain_text_lines):
            duration = max(3.5, min(7.0, len(text) * 0.45))
            words = dictionary_service.segment_and_annotate_line(text)
            pinyin_assembled = " ".join(w.get("pinyin", "") for w in words if not w.get("isPunctuation", False))
            parsed_lines.append({
                "id": i,
                "startTime": round(current_time, 2),
                "endTime": round(current_time + duration, 2),
                "hanzi": text,
                "pinyin": pinyin_assembled,
                "english": "Click line or word for English definitions",
                "words": words
            })
            current_time += duration + 0.5

    return parsed_lines


@app.route("/api/parse-lrc", methods=["POST"])
def parse_lrc():
    """Parses standard LRC lyrics or plain text lyrics, connecting with Pinyin, translation, and word tokens."""
    data = request.get_json() or {}
    song_id = data.get("songId")
    lrc_text = data.get("lrcText", "")

    if not song_id:
        return jsonify({"error": "Missing songId"}), 400
    if not lrc_text.strip():
        return jsonify({"error": "Empty lyrics content"}), 400

    custom_songs = load_custom_songs()
    target_song = None
    for s in custom_songs:
        if s["id"] == song_id:
            target_song = s
            break

    if not target_song:
        return jsonify({"error": "Song not found"}), 404

    parsed_lines = parse_lrc_text_into_lines(lrc_text)

    # If Gemini API key is available, attempt line translation with Gemini 3.5 Flash-Lite
    api_key = data.get("apiKey") or request.headers.get("X-Gemini-API-Key") or os.environ.get("GEMINI_API_KEY")
    if api_key and parsed_lines:
        try:
            parsed_lines = gemini_service.translate_lyrics(
                lines=parsed_lines,
                title=target_song.get("title", ""),
                artist=target_song.get("artist", ""),
                api_key=api_key,
                model="gemini-3.5-flash-lite"
            )
        except Exception as e:
            print(f"Gemini translation notice during parse_lrc: {e}")

    target_song["lines"] = parsed_lines
    save_custom_songs(custom_songs)
    return jsonify(target_song)


@app.route("/api/import-youtube", methods=["POST"])
def import_youtube():
    """
    Automated closed-loop YouTube import:
    1. Queries Gemini 3.5 Flash-Lite on YouTube metadata to isolate canonical Chinese track and artist.
    2. Queries LRCLIB for synchronized lyrics.
    3. Downloads YouTube audio stream via yt-dlp to uploads/.
    4. Generates Pinyin, dictionary tokens, and line translations via Gemini 3.5 Flash-Lite.
    5. Persists the new song in data/songs.json.
    """
    data = request.get_json() or {}
    youtube_url = (data.get("youtubeUrl") or "").strip()
    api_key = data.get("apiKey") or request.headers.get("X-Gemini-API-Key") or os.environ.get("GEMINI_API_KEY")

    if not youtube_url:
        return jsonify({"error": "Please provide a valid YouTube URL"}), 400

    yt_id = youtube_lrclib_service.extract_youtube_id(youtube_url)
    if not yt_id:
        return jsonify({"error": "Could not recognize a valid YouTube URL or Video ID"}), 400

    song_id = f"song-{uuid.uuid4().hex[:8]}"

    try:
        # Step 1: Retrieve basic YouTube info
        video_info = youtube_lrclib_service.get_youtube_video_info(youtube_url)
        raw_title = video_info.get("title", "YouTube Song")
        raw_author = video_info.get("author", "")

        # Step 2: Use Gemini 3.5 Flash-Lite to extract clean Chinese track and artist
        meta = gemini_service.extract_song_metadata_from_youtube(
            video_title=raw_title,
            author=raw_author,
            api_key=api_key
        )
        track_name = meta.get("track_name") or raw_title
        artist_name = meta.get("artist_name") or raw_author or "Mandarin Artist"

        # Step 3: Fetch synchronized lyrics from LRCLIB
        duration = video_info.get("duration")
        lrclib_data = youtube_lrclib_service.fetch_lrclib_lyrics(
            track_name=track_name,
            artist_name=artist_name,
            duration=duration
        )

        lrc_content = ""
        if lrclib_data:
            lrc_content = lrclib_data.get("syncedLyrics") or lrclib_data.get("plainLyrics") or ""

        # Step 4: Download YouTube audio via yt-dlp
        audio_info = youtube_lrclib_service.download_youtube_audio(
            youtube_url=youtube_url,
            output_dir=UPLOAD_FOLDER,
            song_id=song_id
        )

        audio_filename = audio_info["filename"]
        audio_filepath = audio_info["filepath"]
        audio_url = f"/uploads/{audio_filename}"

        # Step 5: Parse lyrics and build annotated lines
        if lrc_content:
            parsed_lines = parse_lrc_text_into_lines(lrc_content)
        else:
            # Fallback placeholder if no lyrics found in LRCLIB
            fallback_text = f"{track_name}\n{artist_name}"
            parsed_lines = parse_lrc_text_into_lines(fallback_text)

        # Step 6: Generate line-by-line English translation with Gemini 3.5 Flash-Lite
        translations_done = False
        if api_key and parsed_lines:
            try:
                print(f"Starting Gemini 3.5 Flash-Lite translation for {len(parsed_lines)} lines...")
                parsed_lines = gemini_service.translate_lyrics(
                    lines=parsed_lines,
                    title=track_name,
                    artist=artist_name,
                    api_key=api_key,
                    model="gemini-3.5-flash-lite"
                )
                translations_done = any(l.get("english") and l["english"] != "Click line or word for English definitions" for l in parsed_lines)
                print(f"Gemini translation finished. Success: {translations_done}")
            except Exception as e:
                print(f"Gemini translation notice during YouTube import: {e}")
        elif not api_key:
            print("Notice: No Gemini API key provided for translation during YouTube import.")

        # Step 7: Create and persist song object
        song_display_title = track_name
        if meta.get("english_title") and meta["english_title"].lower() != track_name.lower():
            song_display_title += f" ({meta['english_title']})"

        new_song = {
            "id": song_id,
            "title": song_display_title,
            "artist": artist_name,
            "audioUrl": audio_url,
            "audioPath": audio_filepath,
            "difficulty": "YouTube Import",
            "isCustom": True,
            "youtubeUrl": youtube_url,
            "hasSyncedLyrics": bool(lrclib_data and lrclib_data.get("syncedLyrics")),
            "lines": parsed_lines
        }

        custom_songs = load_custom_songs()
        custom_songs.append(new_song)
        save_custom_songs(custom_songs)

        return jsonify({
            "success": True,
            "message": f"Successfully imported '{song_display_title}'!",
            "song": new_song
        })

    except Exception as e:
        print(f"Error importing YouTube song: {e}")
        return jsonify({"error": f"Failed to import from YouTube: {str(e)}"}), 500


@app.route("/api/save-sync", methods=["POST"])
def save_sync():
    """Saves user-modified or tap-synced lyric timestamps."""
    data = request.get_json() or {}
    song_id = data.get("songId")
    lines = data.get("lines", [])

    custom_songs = load_custom_songs()
    target_song = None
    for s in custom_songs:
        if s["id"] == song_id:
            target_song = s
            break

    if not target_song:
        return jsonify({"error": "Song not found"}), 404

    # Enforce valid and connected end times for playback synchronization
    for i in range(len(lines)):
        if i + 1 < len(lines):
            if lines[i + 1].get("startTime", 0) > lines[i].get("startTime", 0):
                lines[i]["endTime"] = round(float(lines[i + 1]["startTime"]), 2)
            elif float(lines[i].get("endTime", 0)) <= float(lines[i].get("startTime", 0)):
                lines[i]["endTime"] = round(float(lines[i].get("startTime", 0)) + 4.0, 2)
        else:
            if float(lines[i].get("endTime", 0)) <= float(lines[i].get("startTime", 0)):
                lines[i]["endTime"] = round(float(lines[i].get("startTime", 0)) + 5.0, 2)

    target_song["lines"] = lines
    save_custom_songs(custom_songs)
    return jsonify({"success": True, "song": target_song})


@app.route("/api/dictionary/lookup", methods=["POST"])
def dictionary_lookup():
    data = request.get_json() or {}
    word = data.get("word", "")
    info = dictionary_service.lookup_word(word)
    if info:
        return jsonify(info)
    return jsonify({"error": "Word not found in local dictionary"}), 404


@app.route("/api/explain-phrase", methods=["POST"])
def explain_phrase():
    data = request.get_json() or {}
    phrase = data.get("phrase", "")
    line_context = data.get("lineContext", "")
    song_title = data.get("songTitle", "")
    api_key = data.get("apiKey")

    try:
        explanation = gemini_service.explain_lyric_phrase(
            phrase=phrase,
            line_context=line_context,
            song_title=song_title,
            api_key=api_key
        )
        return jsonify(explanation)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/vocab", methods=["GET", "POST"])
def handle_vocab():
    if request.method == "GET":
        return jsonify({"vocab": load_saved_vocab()})
    
    # POST
    data = request.get_json() or {}
    word = data.get("hanzi")
    if not word:
        return jsonify({"error": "Missing word"}), 400
    
    vocab_list = load_saved_vocab()
    # Check if already exists
    for item in vocab_list:
        if item.get("hanzi") == word:
            return jsonify({"message": "Word already in vocabulary deck", "vocab": vocab_list})
    
    item = {
        "id": uuid.uuid4().hex[:8],
        "hanzi": word,
        "traditional": data.get("traditional", word),
        "pinyin": data.get("pinyin", ""),
        "tone": data.get("tone", 1),
        "translation": data.get("translation", ""),
        "hsk": data.get("hsk", 1),
        "songTitle": data.get("songTitle", ""),
        "lineContext": data.get("lineContext", "")
    }
    vocab_list.insert(0, item)
    save_saved_vocab(vocab_list)
    return jsonify({"success": True, "vocab": vocab_list})


@app.route("/api/vocab/<word_id>", methods=["DELETE"])
def delete_vocab(word_id):
    vocab_list = load_saved_vocab()
    vocab_list = [v for v in vocab_list if v.get("id") != word_id and v.get("hanzi") != word_id]
    save_saved_vocab(vocab_list)
    return jsonify({"success": True, "vocab": vocab_list})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8765, debug=True)
