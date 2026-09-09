# HuayuKaraoke • 华语K歌学堂
**Learn Mandarin Chinese Through Songs with Karaoke-Style Synchronized Lyrics, AI Alignment, & Interactive Dictionary**

---

## Features

- **Karaoke-Style Synchronized Playback**:
  - 3-tier synchronized lyric lines: **Pinyin** with accurate tone accents, large **Chinese Characters (Hanzi)**, and natural **English Translations**.
  - **Spotlight Mode**: Active line is highlighted in a spotlight card and scrolled smoothly into center view.
  - **Click-to-Seek**: Click any lyric line on the stage to jump playback straight to that timestamp.
- **Precision Keyboard Navigation**:
  - `Left Arrow (←)` / `Right Arrow (→)`: Jump backward/forward line-by-line.
  - `Up Arrow (↑)` or `R`: Replay current line from start.
  - `Down Arrow (↓)` or `L`: Toggle **A-B Line Loop Mode** (repeats current line indefinitely for shadowing & pronunciation practice).
  - `Spacebar`: Play / Pause.
  - `[` and `]`: Adjust audio playback speed (`0.75x`, `0.85x`, `1.0x`, `1.2x`).
- **Interactive Pop-up Dictionary**:
  - Hover or click on any word or character in the lyrics.
  - Displays:
    - Simplified & Traditional characters
    - Pinyin with tone classification
    - Native Mandarin speech audio pronunciation (via Web Speech API `speechSynthesis`)
    - English definition and grammatical part of speech
    - HSK Level badge (HSK 1-6)
    - "Save to Vocab" button
    - "AI Deep Dive" button for Gemini-powered cultural nuances, idioms, and example sentences.
- **Audio Upload & Lyric Alignment**:
  - Upload your own MP3, WAV, M4A, or OGG audio files.
  - **Gemini AI Auto-Alignment**: Automatically recognizes songs or transcribes audio, aligns timestamps, generates Pinyin with tone marks, translates to English, and breaks down vocabulary.
  - **LRC / Text Import**: Paste standard timestamped `.lrc` lyrics (`[00:12.50]...`) to instantly synchronize.
  - **Tap-to-Sync Editor**: Built-in interactive editor where you can listen to any song and tap `[Stamp Current Time]` or Spacebar to calibrate line timestamps!
- **Pedagogical Practice & Toggles**:
  - **Tone Colors Toggle**: Visually highlights 1st tone (blue), 2nd tone (green), 3rd tone (orange), 4th tone (red), and neutral tone (gray).
  - **Pinyin Blinder Toggle**: Hide Pinyin to test your character recognition recall.
  - **English Comprehension Toggle**: Hide English to challenge your listening skills.
  - **Script Toggle**: Instant toggle between Simplified (简体) and Traditional (繁體).
  - **Flashcard Review**: Flip cards with audio pronunciation to review saved vocabulary.
  - **Mandarin Lyric Quiz**: Interactive fill-in-the-blank listening quiz with audio snippets and instant scoring.

---

## Quick Start

### 1. Launch the Server
In terminal:
```bash
cd /Users/ryanchu/.gemini/antigravity/scratch/mandarin-karaoke
./start.sh
# or: python3 app.py
```

### 2. Open the Web App
Open your web browser and navigate to:
```
http://localhost:8765
```

### 3. Immediate Out-of-the-Box Demo
The app comes pre-loaded with the iconic Mandarin classic:
- **"月亮代表我的心" (*The Moon Represents My Heart* - Teresa Teng)** complete with synthesized backing melody, millisecond timestamps, pinyin, characters, English translations, and vocabulary breakdown!
- No API key is needed to start playing and practicing immediately.

### 4. Configure Gemini API Key (Optional for Custom Uploads & AI Deep Dive)
Click the **Settings** gear icon in the top navigation bar and paste your Gemini API Key. It will be stored securely in your browser's local storage.

---

## Directory Structure

```
mandarin-karaoke/
├── app.py                      # Flask REST API backend & static file server
├── gemini_service.py           # Gemini 2.5 Flash / Transcribe integration
├── dictionary_service.py       # Pinyin tone converter, HSK lookup & word tokenizer
├── sample_data.py              # Pre-loaded sample songs with timestamps
├── generate_sample_audio.py    # Harmonic audio synthesizer for demo songs
├── test_app.py                 # Automated unit and integration test suite
├── start.sh                    # One-click startup shell script
├── static/
│   ├── audio/                  # Audio tracks (.wav, .mp3)
│   ├── css/styles.css          # Custom karaoke styling, tone colors, animations
│   └── js/
│       ├── app.js              # Orchestrator & UI event manager
│       ├── player.js           # Audio playback & real-time sync engine
│       ├── keyboard.js         # Arrow keys & keyboard shortcuts
│       ├── dictionary.js       # Pop-up dictionary & Web Speech audio
│       ├── sync_editor.js      # Tap-to-sync lyric editor
│       └── quiz.js             # Flashcards & fill-in-the-blank quiz
├── templates/
│   └── index.html              # Modern responsive HTML5 application
├── uploads/                    # User uploaded audio files
└── data/                       # User saved custom songs and vocabulary
```
