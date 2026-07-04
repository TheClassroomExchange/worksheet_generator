"""Word -> small picture resolver for phonics worksheets.

Two interchangeable backends feed the existing ``image`` part of the worksheet:
  - ``openmoji``  : OpenMoji *black* line-art SVGs (CC BY-SA 4.0). Deterministic,
                    free, B&W outline ≈ the "I Can Read Sentences" clip-art look.
  - ``ai``        : per-word B&W line drawing via an image-gen API (OpenAI Images
                    or Stability), used only if the matching API key is set.

Both return a local file path (cached) or None when no picture is available, so a
worksheet never renders a wrong/placeholder picture silently.
"""
from __future__ import annotations

import json
import os
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPENMOJI_DIR = ROOT / "assets" / "openmoji_black"
AI_DIR = ROOT / "assets" / "ai_line_art"
OPENMOJI_RAW = "https://raw.githubusercontent.com/hfg-gmuend/openmoji/master/black/svg/{hex}.svg"

# Curated decodable-noun -> emoji map. Extend as the catalogue grows; words absent
# here return None (author then picks a different decodable word or supplies a src).
WORD_EMOJI: dict[str, str] = {
    # sh
    "shark": "🦈", "shell": "🐚", "ship": "🚢", "fish": "🐟", "sheep": "🐑",
    "shoe": "👟", "shirt": "👕", "shop": "🏪", "brush": "🪥", "dish": "🍽",
    # animals / k-cvc
    "cat": "🐱", "dog": "🐶", "pig": "🐷", "hen": "🐔", "fox": "🦊", "ant": "🐜",
    "bug": "🐛", "bee": "🐝", "rat": "🐀", "cow": "🐮", "duck": "🦆", "frog": "🐸",
    "bat": "🦇", "owl": "🦉", "crab": "🦀", "snail": "🐌",
    # objects
    "sun": "☀", "map": "🗺", "bus": "🚌", "van": "🚐", "jet": "✈", "cup": "☕",
    "pen": "🖊", "bed": "🛏", "box": "📦", "key": "🔑", "ball": "⚽", "drum": "🥁",
    "hat": "🎩", "bell": "🔔", "fan": "🪭", "lamp": "💡", "ring": "💍", "gift": "🎁",
    "leaf": "🍃", "tree": "🌳", "star": "⭐", "moon": "🌙", "rain": "🌧", "snow": "❄",
    "boat": "⛵", "train": "🚆", "car": "🚗", "kite": "🪁", "cake": "🎂", "rose": "🌹",
    "nest": "🪺", "egg": "🥚", "milk": "🥛", "jam": "🍓", "ham": "🍖", "nut": "🥜",
    "corn": "🌽", "plum": "🫐", "fig": "🍇", "pot": "🍲", "mug": "☕", "sock": "🧦",
    # people / body
    "hand": "✋", "foot": "🦶", "lips": "👄", "chin": "🧒", "king": "🤴", "queen": "👸",
    "mouse": "🐭", "milk": "🥛", "mug": "☕", "moon": "🌙",
    # mascots / header
    "owl": "🦉", "book": "📖", "books": "📚", "pencil": "✏", "graduate": "🎓",
}


class ImageBackendUnavailable(RuntimeError):
    pass


def _trim_white(path: Path, pad: int = 12) -> None:
    """Crop surrounding white margin so the subject fills the frame (AI images
    arrive centered in a large white canvas; OpenMoji icons already fill theirs)."""
    try:
        from PIL import Image, ImageChops
    except Exception:
        return
    im = Image.open(path).convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if not bbox:
        return
    l, t, r, b = bbox
    l, t = max(0, l - pad), max(0, t - pad)
    r, b = min(im.width, r + pad), min(im.height, b + pad)
    im.crop((l, t, r, b)).save(path)


def _emoji_hex(emoji: str) -> str:
    cps = [f"{ord(c):X}" for c in emoji if ord(c) != 0xFE0F]  # drop variation selector
    return "-".join(cps)


def _openmoji(word: str) -> Path | None:
    emoji = WORD_EMOJI.get(word.lower())
    if not emoji:
        return None
    hexname = _emoji_hex(emoji)
    OPENMOJI_DIR.mkdir(parents=True, exist_ok=True)
    dst = OPENMOJI_DIR / f"{hexname}.svg"
    if not dst.exists():
        url = OPENMOJI_RAW.format(hex=hexname)
        data = _http_get(url)
        if not data or b"<svg" not in data[:200]:
            return None
        dst.write_bytes(data)
    return dst


def _urlopen_tls(req, timeout: int = 120) -> bytes:
    """urlopen with a working TLS context (system Python lacks root certs).
    Tries certifi; falls back to curl for the same request (POST-aware)."""
    try:
        import ssl, certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.read()
    except Exception:
        cmd = ["curl", "-sS", "--fail", "-X", req.get_method(), req.full_url]
        for k, v in req.header_items():
            cmd += ["-H", f"{k}: {v}"]
        if req.data:
            cmd += ["--data-binary", "@-"]
        out = subprocess.run(cmd, input=req.data, capture_output=True, timeout=timeout + 30)
        if out.returncode != 0:
            raise ImageBackendUnavailable(f"image API call failed: {out.stderr.decode()[:300]}")
        return out.stdout


def _http_get(url: str) -> bytes | None:
    """GET with working TLS. macOS system Python lacks root certs, so prefer curl
    (uses the system trust store); fall back to certifi-backed urllib."""
    try:
        out = subprocess.run(["curl", "-sL", "--fail", url], capture_output=True, timeout=30)
        if out.returncode == 0 and out.stdout:
            return out.stdout
    except Exception:
        pass
    try:
        import ssl, certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen(url, timeout=30, context=ctx) as r:
            return r.read()
    except Exception:
        return None


# Animals / people / creatures get a cute kawaii FACE; everything else (objects,
# food, nature) is drawn cute & rounded but WITHOUT a face.
_ANIMATE = {
    "cat", "dog", "pig", "hen", "fox", "ant", "bug", "bee", "rat", "cow", "duck",
    "frog", "bat", "owl", "crab", "snail", "shark", "fish", "sheep", "mouse",
    "hawk", "chick", "chimp", "lion", "tiger", "bear", "deer", "goat", "horse",
    "seal", "whale", "shrimp", "dolphin", "penguin", "koala", "panda", "rabbit",
    "hamster", "snake", "worm", "fly", "ladybug", "spider", "mole", "hippo",
    "zebra", "giraffe", "monkey", "kangaroo", "elephant", "turtle", "puppy",
    "kitten", "pup", "cub", "calf", "lamb", "foal", "joey", "octopus", "squid",
    "king", "queen", "baby", "boy", "girl", "man", "kid", "chef", "doctor",
    "dad", "mom", "nan", "pup", "vet", "clown", "dragon", "unicorn", "fairy",
    # animals/people that were rendering faceless (missing from the set → OBJECT
    # prompt); added so they get the kawaii FACE prompt on (re)generation.
    "bird", "ghost", "granddaughter",
}

_KAWAII_FACE = (
    "cute kawaii chibi style, simple black and white line drawing of a {w}, "
    "rounded friendly character with a happy smiling face and big cute sparkly eyes, "
    "thick clean bold outlines, minimal, coloring-book style, plain white background, "
    "centered, no text, no shading")
_KAWAII_OBJECT = (
    "cute kawaii style, simple rounded black and white line drawing of a {w}, "
    "soft rounded friendly shapes, thick clean bold outlines, minimal, coloring-book style, "
    "plain white background, centered, no text, NO face, no eyes, no shading")


def _is_animate(word: str) -> bool:
    w = word.lower()
    return w in _ANIMATE or w.rstrip("s") in _ANIMATE


def _ai(word: str, *, style: str | None = None) -> Path | None:
    AI_DIR.mkdir(parents=True, exist_ok=True)
    dst = AI_DIR / f"{word.lower()}.png"
    if dst.exists():
        return dst
    if style:
        prompt = f"A {style} of a {word}."
    else:
        tmpl = _KAWAII_FACE if _is_animate(word) else _KAWAII_OBJECT
        prompt = tmpl.format(w=word)
    okey = os.environ.get("OPENAI_API_KEY")
    skey = os.environ.get("STABILITY_API_KEY")
    orkey = os.environ.get("OPENROUTER_API_KEY")
    if orkey:
        import base64
        model = os.environ.get("OPENROUTER_IMAGE_MODEL", "google/gemini-2.5-flash-image")
        body = json.dumps({"model": model,
                           "messages": [{"role": "user", "content": prompt}],
                           "modalities": ["image", "text"]}).encode()
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions", body,
            {"Authorization": f"Bearer {orkey}", "Content-Type": "application/json",
             "HTTP-Referer": "https://theclassroomexchange.ca", "X-Title": "TCE Phonics"})
        out = json.loads(_urlopen_tls(req, timeout=180))
        # OpenRouter returns generated images under message.images[].image_url.url (data URI)
        msg = out["choices"][0]["message"]
        imgs = msg.get("images") or []
        if not imgs:
            raise ImageBackendUnavailable(f"OpenRouter model {model} returned no image for {word!r}")
        data_uri = imgs[0]["image_url"]["url"]
        b64 = data_uri.split(",", 1)[1]
        dst.write_bytes(base64.b64decode(b64))
        _trim_white(dst)
        return dst
    if okey:
        import base64
        body = json.dumps({"model": "gpt-image-1", "prompt": prompt,
                           "size": "1024x1024", "n": 1}).encode()
        req = urllib.request.Request("https://api.openai.com/v1/images/generations", body,
                                     {"Authorization": f"Bearer {okey}", "Content-Type": "application/json"})
        out = json.loads(_urlopen_tls(req, timeout=180))
        dst.write_bytes(base64.b64decode(out["data"][0]["b64_json"]))
        _trim_white(dst)
        return dst
    if skey:
        boundary = "----phonicsboundary7MA4YWxk"
        req = urllib.request.Request(
            "https://api.stability.ai/v2beta/stable-image/generate/core",
            data=_multipart({"prompt": prompt, "output_format": "png", "style_preset": "line-art"}),
            headers={"Authorization": f"Bearer {skey}", "Accept": "image/*",
                     "Content-Type": f"multipart/form-data; boundary={boundary}"})
        dst.write_bytes(_urlopen_tls(req, timeout=180))
        _trim_white(dst)
        return dst
    raise ImageBackendUnavailable(
        "No image-gen API key (OPENAI_API_KEY or STABILITY_API_KEY) set for the AI backend.")


def _multipart(fields: dict) -> bytes:  # minimal multipart/form-data for Stability
    boundary = "----phonicsboundary7MA4YWxk"
    parts = []
    for k, v in fields.items():
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n")
    parts.append(f"--{boundary}--\r\n")
    return "".join(parts).encode()


def resolve(word: str, backend: str = "openmoji") -> Path | None:
    """Return a local image path for ``word`` using ``backend`` ('openmoji'|'ai'), or None."""
    if backend == "openmoji":
        return _openmoji(word)
    if backend == "ai":
        return _ai(word)
    raise ValueError(f"unknown backend {backend!r}")


def ai_available() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY") or os.environ.get("STABILITY_API_KEY")
                or os.environ.get("OPENROUTER_API_KEY"))


if __name__ == "__main__":
    import sys
    for w in sys.argv[1:]:
        print(w, "->", resolve(w, "openmoji"))
