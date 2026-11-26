"""Voice-over provider for each dialogue line.

Order of preference:
1. A recorded file you place at audio/<episode>/<scene_no>_<line_no>.(mp3|wav|m4a)
2. Online TTS, if installed: edge-tts (best Hindi voices) or gTTS
3. Silent track, duration estimated from text length (video still renders)
"""
import asyncio
import subprocess
from pathlib import Path

EXTS = (".mp3", ".wav", ".m4a")


def audio_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def estimate_duration(text: str) -> float:
    # ~2.5 words/second for relaxed Hindi narration, minimum 1.5s
    return max(1.5, len(text.split()) / 2.5 + 0.4)


def _edge_tts(text, voice, out):
    import edge_tts
    asyncio.run(edge_tts.Communicate(text, voice).save(str(out)))


def _gtts(text, out):
    from gtts import gTTS
    gTTS(text=text, lang="hi").save(str(out))


def get_line_audio(episode, scene_no, line_no, text, voice, cache_dir: Path):
    """Return (audio_path or None, duration_seconds)."""
    base = f"{scene_no:02d}_{line_no:02d}"
    for ext in EXTS:
        p = Path("audio") / episode / (base + ext)
        if p.exists():
            return p, audio_duration(p)

    cache_dir.mkdir(parents=True, exist_ok=True)
    out = cache_dir / f"{base}.mp3"
    if out.exists():
        return out, audio_duration(out)
    try:
        try:
            _edge_tts(text, voice, out)
        except ImportError:
            _gtts(text, out)
        return out, audio_duration(out)
    except Exception as e:  # not installed / offline
        print(f"  [tts] no voice for line {base} ({type(e).__name__}); using silent timing")
        return None, estimate_duration(text)
