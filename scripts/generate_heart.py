"""Build resumable static Heart clips from [{"id": ..., "text": ...}] jobs.

Run with the local Kokoro Python runtime, not on Vercel. --limit caps the
number of newly generated clips; previously verified clips remain reusable.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
import re
from pathlib import Path

import numpy as np
import soundfile as sf


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_audio(path):
    info = sf.info(path)
    if (info.samplerate, info.channels, info.subtype, info.format) != (
        24000, 1, "PCM_16", "WAV"
    ):
        raise ValueError(f"Unexpected audio format: {path}")
    samples, rate = sf.read(path, dtype="float32")
    if samples.size <= 9600 or not np.isfinite(samples).all():
        raise ValueError(f"Empty or invalid audio: {path}")
    if float(np.max(np.abs(samples))) <= 0.01:
        raise ValueError(f"No audible signal: {path}")
    return round(len(samples) / rate, 6)


def save_manifest(path, config, clips, jobs):
    ordered = [clips[job["id"]] for job in jobs if job["id"] in clips]
    manifest = {
        "schemaVersion": SCHEMA_VERSION,
        "voice": config["voice"],
        "language": config["language"],
        "model": config["model"],
        "config": config,
        "complete": len(ordered) == len(jobs),
        "requestedClips": len(jobs),
        "clips": ordered,
    }
    # Stable content-derived version also changes when clip text/audio changes.
    canonical = json.dumps(manifest, ensure_ascii=False, sort_keys=True)
    manifest["version"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    temp = path.with_suffix(".json.tmp")
    temp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)
    # Load this external script before the player, so the first mobile click
    # can call audio.play() directly without awaiting a manifest request.
    script_path = path.with_suffix(".js")
    script_temp = script_path.with_suffix(".js.tmp")
    script_temp.write_text(
        "window.IFR_HEART_MANIFEST = "
        + json.dumps(manifest, ensure_ascii=True, separators=(",", ":"))
        + ";\n", encoding="utf-8"
    )
    os.replace(script_temp, script_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=Path, default=ROOT / "output/heart-jobs.json")
    parser.add_argument("--model-dir", type=Path,
                        default=Path(os.environ.get("LOCALAPPDATA", "")) / "Temp/ifr-heart-runtime")
    parser.add_argument("--limit", type=int, help="Maximum new clips to generate (0 validates reuse only)")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 0:
        parser.error("--limit must be zero or greater")

    jobs = json.loads(args.jobs.read_text(encoding="utf-8-sig"))
    if not isinstance(jobs, list) or not jobs:
        raise ValueError("Jobs must be a nonempty JSON list")
    seen = set()
    for job in jobs:
        if not isinstance(job, dict) or not isinstance(job.get("id"), str):
            raise ValueError("Each job needs a string id")
        name = job["id"]
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,119}", name):
            raise ValueError(f"Unsafe clip id: {name!r}")
        if name.upper() in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}:
            raise ValueError(f"Reserved clip id: {name}")
        if name.lower() in seen:
            raise ValueError(f"Duplicate clip id: {name}")
        seen.add(name.lower())
        if not isinstance(job.get("text"), str) or not job["text"].strip():
            raise ValueError(f"Missing text: {name}")

    model_path = args.model_dir / "kokoro-v1.0.onnx"
    voices_path = args.model_dir / "voices-v1.0.bin"
    for path in (model_path, voices_path):
        if not path.is_file():
            raise FileNotFoundError(f"Required local model file not found: {path}")
    config = {
        "generatorVersion": 1,
        "packages": {package: importlib.metadata.version(package) for package in
                     ("kokoro-onnx", "onnxruntime", "numpy", "soundfile")},
        "model": "Kokoro v1.0",
        "modelSha256": sha256(model_path),
        "voicesSha256": sha256(voices_path),
        "voice": "af_heart",
        "language": "en-us",
        "speed": 0.9,
        "sampleRate": 24000,
        "channels": 1,
        "subtype": "PCM_16",
        "leadingSilenceSeconds": 0.15,
        "trailingSilenceSeconds": 0.25,
    }
    out = ROOT / "assets/audio"
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "manifest.json"
    previous = {}
    if manifest_path.exists():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            if data.get("schemaVersion") == SCHEMA_VERSION and data.get("config") == config:
                previous = {clip["id"]: clip for clip in data["clips"]}
        except (ValueError, KeyError, TypeError) as exc:
            print(f"Manifest cannot be reused: {exc}", flush=True)

    clips = {}
    for job in jobs:
        name, text = job["id"], job["text"]
        old = previous.get(name)
        file = f"assets/audio/{name}.wav"
        path = out / f"{name}.wav"
        if old and old.get("text") == text and old.get("file") == file and path.is_file():
            try:
                seconds = inspect_audio(path)
                if old.get("sha256") == sha256(path) and old.get("seconds") == seconds:
                    clips[name] = old
            except (ValueError, RuntimeError, OSError):
                pass
    save_manifest(manifest_path, config, clips, jobs)
    print(f"Verified reusable clips: {len(clips)}/{len(jobs)}", flush=True)

    engine = None
    generated = 0
    for job in jobs:
        name, text = job["id"], job["text"]
        if name in clips:
            continue
        if args.limit is not None and generated >= args.limit:
            break
        if engine is None:
            from kokoro_onnx import Kokoro
            engine = Kokoro(str(model_path), str(voices_path))
        samples, rate = engine.create(text, voice="af_heart", speed=0.9, lang="en-us")
        samples = np.asarray(samples, dtype=np.float32)
        if rate != 24000 or samples.ndim != 1 or not samples.size:
            raise ValueError(f"Unexpected generated format: {name}")
        if not np.isfinite(samples).all() or float(np.max(np.abs(samples))) <= 0.01:
            raise ValueError(f"Invalid or inaudible synthesis: {name}")
        if float(np.max(np.abs(samples))) > 1:
            raise ValueError(f"Synthesis would clip in PCM16: {name}")
        samples = np.concatenate((np.zeros(3600, dtype=np.float32), samples,
                                  np.zeros(6000, dtype=np.float32)))
        path = out / f"{name}.wav"
        temp = out / f"{name}.wav.tmp"
        sf.write(temp, samples, rate, format="WAV", subtype="PCM_16")
        seconds = inspect_audio(temp)
        digest = sha256(temp)
        os.replace(temp, path)
        clips[name] = {"id": name, "text": text, "seconds": seconds,
                       "file": f"assets/audio/{name}.wav", "sha256": digest}
        save_manifest(manifest_path, config, clips, jobs)
        generated += 1
        print(f"{len(clips)}/{len(jobs)} {name}: {seconds:.3f}s", flush=True)
    print(f"Done: generated={generated}; verified={len(clips)}/{len(jobs)}; complete={len(clips) == len(jobs)}", flush=True)


if __name__ == "__main__":
    main()
