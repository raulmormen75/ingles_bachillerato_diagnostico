"""Validate Heart jobs, manifest metadata and WAV files using only the stdlib.

--allow-partial accepts missing jobs while generation is running, but checks
every clip in the atomically published manifest snapshot. It does not inspect
unlisted files that the generator may currently be writing.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import wave


ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_strings(value, label):
    if isinstance(value, str):
        value.encode("utf-8", errors="strict")
        require(not any(marker in value for marker in
                        ("\ufffd", "\u00c3", "\u00c2", "\u00e2\u20ac", "\u00f0\u0178")),
                f"Possible encoding corruption in {label}")
        require(not any(ord(c) < 32 and c not in "\n\r\t" for c in value),
                f"Unexpected control character in {label}")
    elif isinstance(value, dict):
        for key, child in value.items():
            check_strings(key, label)
            check_strings(child, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            check_strings(child, f"{label}[{index}]")


def load_json(path):
    value = json.loads(path.read_text(encoding="utf-8-sig", errors="strict"))
    check_strings(value, path.name)
    return value


def validate(jobs_path, manifest_path, allow_partial):
    jobs = load_json(jobs_path)
    manifest = load_json(manifest_path)
    require(isinstance(jobs, list) and jobs, "Jobs must be a nonempty list")
    expected = {}
    for job in jobs:
        require(isinstance(job, dict), "Invalid job record")
        name, text = job.get("id"), job.get("text")
        require(isinstance(text, str) and text.strip(), "Missing job text")
        digest_id = "heart-" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:20]
        require(name == digest_id, f"Job id does not match its text: {name}")
        require(name not in expected, f"Duplicate job id: {name}")
        expected[name] = text

    require(isinstance(manifest, dict), "Manifest must be an object")
    require(manifest.get("schemaVersion") == 1, "Unexpected schemaVersion")
    for key, value in {"voice": "af_heart", "language": "en-us", "model": "Kokoro v1.0"}.items():
        require(manifest.get(key) == value, f"Unexpected manifest {key}")
    config = manifest.get("config")
    require(isinstance(config, dict), "Missing config")
    for key, value in {"voice": "af_heart", "language": "en-us", "model": "Kokoro v1.0",
                       "speed": 0.9, "sampleRate": 24000, "channels": 1,
                       "subtype": "PCM_16", "leadingSilenceSeconds": 0.15,
                       "trailingSilenceSeconds": 0.25}.items():
        require(config.get(key) == value, f"Unexpected config {key}")
    for key in ("modelSha256", "voicesSha256"):
        require(isinstance(config.get(key), str) and re.fullmatch(r"[0-9a-f]{64}", config[key]),
                f"Invalid config {key}")
    require(manifest.get("requestedClips") == len(jobs), "requestedClips differs from jobs")
    clips = manifest.get("clips")
    require(isinstance(clips, list), "Manifest clips must be a list")
    require(type(manifest.get("complete")) is bool, "complete must be boolean")
    canonical_manifest = {k: v for k, v in manifest.items() if k != "version"}
    version = hashlib.sha256(json.dumps(canonical_manifest, ensure_ascii=False,
                                       sort_keys=True).encode("utf-8")).hexdigest()[:16]
    require(manifest.get("version") == version, "Manifest version hash mismatch")

    seen = set()
    total_bytes = 0
    total_seconds = 0.0
    for clip in clips:
        require(isinstance(clip, dict), "Invalid clip record")
        name = clip.get("id")
        require(isinstance(name, str) and name in expected, f"Unexpected clip id: {name}")
        require(name not in seen, f"Duplicate manifest clip: {name}")
        seen.add(name)
        require(clip.get("text") == expected[name], f"Text mismatch: {name}")
        relative = f"assets/audio/{name}.wav"
        require(clip.get("file") == relative, f"Unexpected or unsafe file path: {name}")
        path = ROOT / relative
        require(path.is_file(), f"Missing WAV: {relative}")
        size = path.stat().st_size
        require(size > 44, f"Empty WAV: {relative}")
        data = path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == clip.get("sha256"), f"WAV hash mismatch: {name}")
        with wave.open(str(path), "rb") as recording:
            require((recording.getnchannels(), recording.getframerate(), recording.getsampwidth(),
                     recording.getcomptype()) == (1, 24000, 2, "NONE"), f"Invalid WAV format: {name}")
            frames = recording.getnframes()
            require(frames > 0, f"No audio frames: {name}")
            pcm = recording.readframes(frames)
            require(len(pcm) == frames * 2, f"Truncated audio frames: {name}")
            require(any(pcm), f"Entirely silent audio: {name}")
            actual_seconds = frames / 24000
        seconds = clip.get("seconds")
        require(type(seconds) in (int, float) and math.isfinite(seconds) and seconds > 0,
                f"Invalid duration: {name}")
        require(abs(seconds - actual_seconds) <= 0.001, f"Duration differs by over 1 ms: {name}")
        total_bytes += size
        total_seconds += actual_seconds

    complete = len(seen) == len(expected)
    require(manifest["complete"] == complete, "complete flag disagrees with actual clip coverage")
    if not allow_partial:
        require(complete, f"Incomplete: {len(seen)}/{len(expected)} clips validated")
    return {"status": "complete" if complete else "partial", "validatedClips": len(seen),
            "requestedClips": len(expected), "missingClips": len(expected) - len(seen),
            "totalBytes": total_bytes, "totalSeconds": round(total_seconds, 6),
            "voice": "af_heart", "format": "WAV mono 24000 Hz PCM16"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=Path, default=ROOT / "output/heart-jobs.json")
    parser.add_argument("--manifest", type=Path, default=ROOT / "assets/audio/manifest.json")
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    try:
        result = validate(args.jobs, args.manifest, args.allow_partial)
    except (OSError, ValueError, TypeError, KeyError, wave.Error, EOFError) as error:
        print(f"FAILED: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
