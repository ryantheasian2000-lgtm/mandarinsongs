"""
Generates synchronized Mandarin vocal singing/spoken lines using macOS native Chinese voice (Tingting),
and mixes them seamlessly with the musical backing track into static/audio/the_moon_represents_my_heart.wav.
"""

import os
import wave
import struct
import subprocess

SAMPLE_RATE = 44100

LYRIC_LINES = [
    (3.6, "你问我爱你有多深"),
    (8.2, "我爱你有几分"),
    (12.0, "我的情也真"),
    (15.8, "我的爱也真"),
    (19.6, "月亮代表我的心"),
    (25.5, "轻轻的一个吻"),
    (30.0, "曾经打动你的心"),
    (33.8, "深深的一段情"),
    (37.6, "叫我思念到如今"),
    (42.0, "你去想一想，你去看一看"),
    (47.5, "月亮代表我的心"),
]

def load_wav_samples(wav_path: str) -> list:
    with wave.open(wav_path, "r") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)
        
        # Unpack 16-bit
        if sampwidth == 2:
            count = len(raw) // 2
            samples = list(struct.unpack(f"<{count}h", raw))
            # If stereo, convert to mono
            if n_channels == 2:
                samples = [(samples[i] + samples[i+1]) // 2 for i in range(0, len(samples), 2)]
            # Simple resample to 44100 if needed
            if framerate != SAMPLE_RATE:
                ratio = SAMPLE_RATE / framerate
                new_len = int(len(samples) * ratio)
                resampled = []
                for i in range(new_len):
                    src_idx = int(i / ratio)
                    resampled.append(samples[min(src_idx, len(samples) - 1)])
                return resampled
            return samples
        return []

def main():
    # 1. First ensure the base music track exists
    base_music_path = "static/audio/music_backing.wav"
    from generate_sample_audio import synthesize_moon_song
    synthesize_moon_song(base_music_path)

    music_samples = load_wav_samples(base_music_path)
    total_len = len(music_samples)
    vocal_track = [0] * total_len

    temp_dir = "data/temp_vocals"
    os.makedirs(temp_dir, exist_ok=True)

    print("Generating vocal lines using Tingting (zh-CN)...")
    for idx, (start_time, text) in enumerate(LYRIC_LINES):
        aiff_path = os.path.join(temp_dir, f"line_{idx}.aiff")
        wav_path = os.path.join(temp_dir, f"line_{idx}.wav")

        # Rate 140 is a gentle, lyrical pacing
        subprocess.run(["say", "-v", "Tingting", "-r", "140", text, "-o", aiff_path], check=True)
        subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16", "-c", "1", "-r", "44100", aiff_path, wav_path], check=True)

        line_samples = load_wav_samples(wav_path)
        start_idx = int(start_time * SAMPLE_RATE)

        # Mix into vocal track
        for i, s in enumerate(line_samples):
            target_idx = start_idx + i
            if target_idx < total_len:
                vocal_track[target_idx] += s

        # Clean up temp files
        if os.path.exists(aiff_path): os.remove(aiff_path)
        if os.path.exists(wav_path): os.remove(wav_path)

    # 2. Master & mix: backing music (0.5) + clear vocals (0.9)
    print("Mastering final vocal + instrumental track...")
    mixed = []
    for i in range(total_len):
        music_val = music_samples[i] * 0.45
        vocal_val = vocal_track[i] * 0.95
        combined = int(music_val + vocal_val)
        clamped = max(-32768, min(32767, combined))
        mixed.append(clamped)

    final_output = "static/audio/the_moon_represents_my_heart.wav"
    with wave.open(final_output, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        packed = struct.pack(f"<{len(mixed)}h", *mixed)
        wf.writeframes(packed)

    print(f"Successfully generated full vocal + instrumental song: {final_output}")

if __name__ == "__main__":
    main()
