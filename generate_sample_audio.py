"""
Synthesizes clean, melodic backing tracks for sample songs
using harmonic acoustic piano/chime synthesis with pure Python stdlib (wave, struct, math).
"""

import wave
import struct
import math
import os

SAMPLE_RATE = 44100

def note_to_freq(note_name: str) -> float:
    """Converts note name like 'C4', 'D#4', 'G3' to Hz."""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    name = note_name.upper()
    octave = int(name[-1])
    key = name[:-1]
    semitone = notes.index(key)
    # A4 is 440Hz, octave 4, key 9
    distance = (octave - 4) * 12 + (semitone - 9)
    return 440.0 * (2.0 ** (distance / 12.0))

def render_tone(freq: float, duration_s: float, volume: float = 0.5) -> list:
    """Renders a piano-like tone with attack, gentle decay, and warm harmonics."""
    num_samples = int(SAMPLE_RATE * duration_s)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Envelope: fast attack (0.02s), exponential decay
        if t < 0.02:
            env = t / 0.02
        else:
            decay_rate = 2.2
            env = math.exp(-decay_rate * (t - 0.02))
        
        # Harmonics (piano / chime timbre)
        val = (
            math.sin(2 * math.pi * freq * t) * 0.6 +
            math.sin(2 * math.pi * freq * 2 * t) * 0.25 +
            math.sin(2 * math.pi * freq * 3 * t) * 0.1 +
            math.sin(2 * math.pi * freq * 4 * t) * 0.05
        )
        sample = int(val * env * volume * 32767)
        sample = max(-32768, min(32767, sample))
        samples.append(sample)
    return samples

def render_rest(duration_s: float) -> list:
    return [0] * int(SAMPLE_RATE * duration_s)

def synthesize_moon_song(output_path: str):
    """
    Synthesizes the melody of 'The Moon Represents My Heart' (月亮代表我的心)
    Key of F major / C major.
    """
    # bpm = 72, 1 beat = 60/72 ≈ 0.833s
    beat = 0.82
    
    # Melody timeline: (note, beats)
    melody = [
        # Intro chords
        ("C4", 1.0), ("E4", 1.0), ("G4", 1.0), ("C5", 1.0), ("REST", 0.5),
        
        # Line 1: 你问我爱你有多深 (03.8s - 08.2s)
        ("E4", 0.5), ("G4", 0.5), ("C5", 0.8), ("D5", 0.5), ("E5", 0.8),
        ("D5", 0.5), ("C5", 0.5), ("A4", 0.5), ("G4", 1.2), ("REST", 0.4),
        
        # Line 2: 我爱你有几分 (08.2s - 12.0s)
        ("E4", 0.5), ("D4", 0.5), ("C4", 0.8), ("C4", 0.5), ("D4", 0.6), ("E4", 1.2), ("REST", 0.4),
        
        # Line 3: 我的情也真 (12.0s - 15.8s)
        ("G4", 0.6), ("E4", 0.6), ("D4", 0.6), ("C4", 0.6), ("D4", 1.4), ("REST", 0.4),
        
        # Line 4: 我的爱也真 (15.8s - 19.6s)
        ("G4", 0.6), ("E4", 0.6), ("D4", 0.6), ("C4", 0.6), ("C4", 1.6), ("REST", 0.4),
        
        # Line 5: 月亮代表我的心 (19.6s - 25.5s)
        ("D4", 0.6), ("E4", 0.6), ("G4", 0.8), ("A4", 0.6), ("G4", 0.8),
        ("E4", 0.6), ("D4", 0.6), ("C4", 1.8), ("REST", 0.8),
        
        # Line 6: 轻轻的一个吻 (25.5s - 30.0s)
        ("E4", 0.5), ("G4", 0.5), ("C5", 0.8), ("D5", 0.5), ("E5", 0.8),
        ("D5", 0.5), ("C5", 0.5), ("A4", 0.5), ("G4", 1.2), ("REST", 0.4),
        
        # Line 7: 曾经打动你的心 (30.0s - 33.8s)
        ("E4", 0.5), ("D4", 0.5), ("C4", 0.8), ("C4", 0.5), ("D4", 0.6), ("E4", 1.2), ("REST", 0.4),
        
        # Line 8: 深深的一段情 (33.8s - 37.6s)
        ("G4", 0.6), ("E4", 0.6), ("D4", 0.6), ("C4", 0.6), ("D4", 1.4), ("REST", 0.4),
        
        # Line 9: 叫我思念到如今 (37.6s - 42.0s)
        ("G4", 0.6), ("E4", 0.6), ("D4", 0.6), ("C4", 0.6), ("C4", 2.0), ("REST", 0.6),
        
        # Line 10: 你去想一想，你去看一看 (42.0s - 47.5s)
        ("G4", 0.5), ("E4", 0.5), ("D4", 0.5), ("C4", 0.5), ("D4", 0.9), ("REST", 0.3),
        ("G4", 0.5), ("E4", 0.5), ("D4", 0.5), ("C4", 0.5), ("C4", 1.4), ("REST", 0.4),
        
        # Line 11: 月亮代表我的心 (47.5s - 54.0s)
        ("D4", 0.6), ("E4", 0.6), ("G4", 0.8), ("A4", 0.6), ("G4", 0.8),
        ("E4", 0.6), ("D4", 0.6), ("C4", 2.5), ("REST", 1.0)
    ]
    
    all_samples = []
    for item in melody:
        note, beats = item
        duration = beats * beat
        if note == "REST":
            all_samples.extend(render_rest(duration))
        else:
            freq = note_to_freq(note)
            all_samples.extend(render_tone(freq, duration, volume=0.55))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with wave.open(output_path, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(SAMPLE_RATE)
        # Pack samples
        packed_data = struct.pack(f"<{len(all_samples)}h", *all_samples)
        wav_file.writeframes(packed_data)

    duration_sec = len(all_samples) / SAMPLE_RATE
    print(f"Generated {output_path}: duration = {duration_sec:.2f}s")
    return duration_sec

if __name__ == "__main__":
    synthesize_moon_song("static/audio/the_moon_represents_my_heart.wav")
