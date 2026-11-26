# Video-creator-
2D animated videos with Hindi voice-over, made from a simple JSON script.
First series: **Danish Ban Gaya YouTuber**.

## Quick start
```bash
python -m vidcreator.render episodes/ep01.json      # -> out/ep01.mp4
```
Needs: Python 3, Pillow (with raqm), ffmpeg/ffprobe. A Devanagari-capable font
(FreeSans) is used for Hindi subtitles.

## Voice-over (3 options, tried in this order)
1. **Your own recordings**: put files in `audio/ep01/` named `<scene>_<line>.mp3|wav|m4a`
   (e.g. `01_02.mp3` = scene 1, line 2).
2. **Auto TTS**: `pip install edge-tts` (Hindi voices like `hi-IN-MadhurNeural`,
   `hi-IN-SwaraNeural`) or `pip install gTTS`. Needs internet.
3. **Silent**: if neither is available, the video renders with timing estimated from the text.

## Script format
See `episodes/ep01.json`: characters (name, colors, voice), scenes (background, cast,
lines with speaker + Hindi text). Add a new episode by copying that file.

## Layout
- `vidcreator/draw.py`   – 2D character and scene drawing
- `vidcreator/tts.py`    – voice-over lookup/generation
- `vidcreator/render.py` – frames -> MP4 with ffmpeg
