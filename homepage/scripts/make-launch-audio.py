"""Generate the original ambient score and restrained UI chimes for the tour."""
from pathlib import Path
import sys
import wave

import numpy as np


RATE = 48_000
DURATION = float(sys.argv[1]) if len(sys.argv) > 1 else 140.0
CHUNK_SECONDS = 1
CHORD_SECONDS = 7.5
CHORDS = [
    [73.42, 110.00, 146.83, 174.61, 220.00, 261.63, 329.63],  # Dm9
    [58.27, 116.54, 146.83, 174.61, 220.00, 293.66, 349.23],  # Bbmaj7
    [43.65, 87.31, 130.81, 174.61, 220.00, 261.63, 329.63],  # Fmaj7
    [65.41, 130.81, 146.83, 196.00, 261.63, 293.66, 392.00],  # Csus2
]
OUTPUT = Path('work/launch-film-score.wav')
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(14133)
chime_times = [3.6, 47.32, 50.12, 63.88, 66.68, 102.4]


def score_chunk(start: float, seconds: int) -> np.ndarray:
    time = start + np.arange(RATE * seconds, dtype=np.float64) / RATE
    chord_index = np.floor(time / CHORD_SECONDS).astype(np.int64) % len(CHORDS)
    within = np.mod(time, CHORD_SECONDS)
    blend = np.clip((within - (CHORD_SECONDS - 1.4)) / 1.4, 0, 1)
    blend = 0.5 - 0.5 * np.cos(blend * np.pi)
    chord_tones = []
    upper_tones = []
    for index, chord in enumerate(CHORDS):
        tones = np.zeros_like(time)
        for voice, frequency in enumerate(chord):
            phase = voice * 0.37 + index * 0.19
            tones += np.sin(2 * np.pi * frequency * time + phase) / (1 + voice * 0.13)
        chord_tones.append(tones)
        upper_tones.append(np.sin(2 * np.pi * chord[4] * 2 * time + index))
    tones = np.stack(chord_tones)
    upper = np.stack(upper_tones)
    next_index = (chord_index + 1) % len(CHORDS)
    current_tones = np.take_along_axis(tones, chord_index[None, :], axis=0)[0]
    next_tones = np.take_along_axis(tones, next_index[None, :], axis=0)[0]
    output = (current_tones * (1 - blend) + next_tones * blend) * 0.013
    # A soft, slow upper harmonic makes the pad audible on small speakers.
    current_upper = np.take_along_axis(upper, chord_index[None, :], axis=0)[0]
    next_upper = np.take_along_axis(upper, next_index[None, :], axis=0)[0]
    output += (current_upper * (1 - blend) + next_upper * blend) * 0.0018

    # Gentle bell notes on a sparse four-beat pattern.
    beat = np.mod(time, 3.0)
    note_index = (np.floor(time / 3.0).astype(np.int64) + np.floor(time / 12.0).astype(np.int64)) % 5
    notes = np.array([440.0, 523.25, 659.25, 587.33, 493.88])[note_index]
    envelope = np.exp(-np.maximum(beat, 0) * 1.8) * np.clip((0.13 - beat) * 30, 0, 1)
    output += np.sin(2 * np.pi * notes * time) * envelope * 0.009

    # Original, quiet two-tone interface chimes at chapter boundaries.
    for point in chime_times:
        local = time - point
        active = (local >= 0) & (local < 0.22)
        if np.any(active):
            decay = np.exp(-local[active] * 18)
            tone = np.sin(2 * np.pi * 880 * local[active]) + 0.45 * np.sin(2 * np.pi * 1318.51 * local[active])
            output[active] += tone * decay * 0.035

    fade_in = np.clip(time / 2.5, 0, 1)
    fade_out = np.clip((DURATION - time) / 4.0, 0, 1)
    output *= np.minimum(fade_in, fade_out)
    # A very low noise floor softens the synthesized tones without masking speech or interface text.
    output += rng.normal(0, 0.00012, size=output.shape)
    return np.clip(output, -0.78, 0.78)


with wave.open(str(OUTPUT), 'wb') as wav:
    wav.setnchannels(2)
    wav.setsampwidth(2)
    wav.setframerate(RATE)
    for start in np.arange(0, DURATION, CHUNK_SECONDS):
        mono = score_chunk(float(start), CHUNK_SECONDS)
        stereo = np.column_stack((mono, mono * 0.985))
        wav.writeframes((stereo * 32767).astype('<i2').tobytes())

print(f'Created original stereo score: {OUTPUT}')
