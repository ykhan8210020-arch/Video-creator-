"""Render an episode JSON into an MP4 (2D animation + Hindi voice-over + subtitles).

Usage:  python -m vidcreator.render episodes/ep01.json [-o out/ep01.mp4]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from . import draw as D
from .tts import get_line_audio

FPS = 24


def render_episode(ep_path: Path, out_path: Path):
    ep = json.loads(ep_path.read_text(encoding="utf-8"))
    name = ep_path.stem
    work = Path("build") / name
    frames = work / "frames"
    frames.mkdir(parents=True, exist_ok=True)
    for old in frames.glob("*.png"):
        old.unlink()

    chars = ep["characters"]
    voice = ep.get("voice", "hi-IN-MadhurNeural")
    n = 0
    timeline = []  # (audio_path or None, start_sec, dur_sec)
    t_global = 0.0

    def save(img):
        nonlocal n
        img.convert("RGB").save(frames / f"{n:05d}.png")
        n += 1

    # title card (2.5s)
    title = D.draw_title_card(ep["title"], ep.get("subtitle", ""))
    for _ in range(int(2.5 * FPS)):
        save(title)
    t_global += 2.5

    for si, scene in enumerate(ep["scenes"], 1):
        positions = {c["id"]: c.get("x", 300 + 400 * i)
                     for i, c in enumerate(scene.get("cast", chars))}
        for li, line in enumerate(scene["lines"], 1):
            text = line["text"]
            speaker = line.get("speaker")
            style_voice = chars.get(speaker, {}).get("voice", voice) if speaker else voice
            audio, dur = get_line_audio(name, si, li, text, style_voice, work / "tts")
            dur += 0.3  # small pause after each line
            if audio:
                timeline.append((audio, t_global, dur))
            for f in range(int(dur * FPS)):
                t = f / FPS
                img = Image.new("RGBA", (D.W, D.H))
                d = ImageDraw.Draw(img, "RGBA")
                D.draw_background(d, scene.get("background", {}))
                for cid, x in positions.items():
                    c = chars[cid]
                    speaking = (cid == speaker) and t < dur - 0.3
                    D.draw_character(d, x, 600, t + (hash(cid) % 7), speaking,
                                     c, line.get("mood", "happy") if cid == speaker else "happy")
                    D.draw_label(d, x, 130, c["name"])
                D.draw_subtitle(d, text)
                save(img)
            t_global += dur

    silent = work / "silent.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", str(frames / "%05d.png"), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", str(silent)], check=True)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not timeline:
        silent.replace(out_path)
        print(f"Done (no voice-over found): {out_path}")
        return

    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent)]
    for a, _, _ in timeline:
        cmd += ["-i", str(a)]
    filt = []
    for i, (_, start, _) in enumerate(timeline, 1):
        ms = int(start * 1000)
        filt.append(f"[{i}:a]adelay={ms}|{ms}[a{i}]")
    mix = "".join(f"[a{i}]" for i in range(1, len(timeline) + 1))
    filt.append(f"{mix}amix=inputs={len(timeline)}:normalize=0[aout]")
    cmd += ["-filter_complex", ";".join(filt), "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-shortest", str(out_path)]
    subprocess.run(cmd, check=True)
    print(f"Done: {out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    ep = Path(a.episode)
    render_episode(ep, Path(a.out) if a.out else Path("out") / (ep.stem + ".mp4"))


if __name__ == "__main__":
    sys.exit(main())
