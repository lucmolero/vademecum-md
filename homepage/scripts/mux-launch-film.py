"""Mux the code-rendered screen recording with its original score."""
from pathlib import Path
import shutil
import subprocess


ffmpeg = shutil.which('ffmpeg')
if not ffmpeg:
    raise SystemExit('Install FFmpeg and make ffmpeg available on PATH.')

recording = Path('work/vademecum-tour-clean.webm')
score = Path('work/launch-film-score.wav')
output = Path('homepage/public/demos/media/vademecum-tour.mp4')
if not recording.is_file() or not score.is_file():
    raise SystemExit('Render the film and generate its score before muxing.')

subprocess.run([
    ffmpeg, '-y', '-loglevel', 'error', '-i', str(recording), '-i', str(score),
    '-map', '0:v:0', '-map', '1:a:0',
    '-af', 'loudnorm=I=-20:TP=-2:LRA=11',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '23',
    '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-r', '30',
    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest',
    '-movflags', '+faststart', str(output),
], check=True)
print(f'Created {output}')
