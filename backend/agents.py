"""
AI Launchpad — the agent crew.

Four specialized agents, each a single focused LLM call to an OpenAI-compatible
endpoint. In this project that endpoint is a Qwen2.5-7B-Instruct model served with
vLLM on an **AMD Developer Cloud GPU** (Fireworks AI, which also runs open models
on AMD GPUs, works unchanged). Every agent is forced to return JSON so the
frontend can render the result reliably.

When no live endpoint is configured, the module runs in OFFLINE mode and serves
kits that were genuinely generated on the AMD GPU (see `kits/`), so the UI can be
demoed without a GPU attached.
"""

import json
import os
import re
import asyncio

import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FIREWORKS_API_KEY", "").strip()
MODEL = os.getenv("FIREWORKS_MODEL", "Qwen/Qwen2.5-7B-Instruct")
BASE_URL = os.getenv("FIREWORKS_BASE_URL", "https://api.fireworks.ai/inference/v1")

# USE_MOCK=true forces offline data even when a key is set.
FORCE_MOCK = os.getenv("USE_MOCK", "").strip().lower() in ("1", "true", "yes")
MOCK_MODE = FORCE_MOCK or not API_KEY

KITS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kits")

# Saved kits, each really generated on an AMD Developer Cloud GPU.
_KEYWORD_KITS = [
    (("student", "part-time", "part time", "campus", "intern"), "kit_students.json"),
    (("coffee", "bean", "barista", "espresso", "brew"), "kit_coffee.json"),
    (("fitness", "workout", "gym", "exercise", "training"), "kit_fitness.json"),
    (("pet", "dog", "cat", "walking", "walker"), "kit_pets.json"),
]
_DEFAULT_KIT = "kit_students.json"

_HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_FALLBACK_PALETTE = ["#0F172A", "#2563EB", "#38BDF8", "#F8FAFC", "#F59E0B"]


# ---------------------------------------------------------------------------
# Robustness helpers
# ---------------------------------------------------------------------------
def _clean_palette(brand: dict) -> dict:
    """Keep only real hex colours.

    Models sometimes drift from the schema and return colours interleaved with
    prose, e.g. ["#FFC107", "A vibrant yellow for energy", "#4CAF50", ...].
    Rendering those strings as swatches breaks the UI, so we filter and dedupe.
    """
    if not isinstance(brand, dict):
        return {}
    raw = brand.get("palette")
    colors, seen = [], set()
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):
                c = item.strip()
                if _HEX_RE.match(c) and c.lower() not in seen:
                    seen.add(c.lower())
                    colors.append(c)
    brand["palette"] = (colors or _FALLBACK_PALETTE)[:5]
    return brand


def _load_offline_kit(idea: str) -> dict:
    """Return a saved AMD-generated kit that best matches the idea."""
    text = (idea or "").lower()
    filename, exact = _DEFAULT_KIT, False
    for keywords, fname in _KEYWORD_KITS:
        if any(k in text for k in keywords):
            filename, exact = fname, True
            break

    with open(os.path.join(KITS_DIR, filename), encoding="utf-8") as f:
        kit = json.load(f)

    kit["brand"] = _clean_palette(kit.get("brand", {}))
    kit["mock"] = True
    kit["offline_exact"] = exact
    return kit


# ---------------------------------------------------------------------------
# Core LLM call
# ---------------------------------------------------------------------------
async def _call_llm(system_prompt: str, user_prompt: str) -> dict:
    """Send one prompt to the model and parse the JSON response."""
    if MOCK_MODE:
        return {}

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 800,
        "response_format": {"type": "json_object"},
    }

    # Retry on transient failures (timeouts, rate limits, 5xx) so a single
    # hiccup never breaks a live demo.
    last_error = None
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    f"{BASE_URL}/chat/completions", headers=headers, json=payload
                )
                resp.raise_for_status()
                data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return _safe_json(content)
        except Exception as e:  # noqa: BLE001 - deliberately broad for resilience
            last_error = e
            if attempt < 2:
                await asyncio.sleep(1.5 * (attempt + 1))

    raise RuntimeError(f"LLM call failed after retries: {last_error}")


def _safe_json(text: str) -> dict:
    """Parse JSON, tolerating stray text or code fences around it."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start : end + 1])
        raise


# ---------------------------------------------------------------------------
# The four agents
# ---------------------------------------------------------------------------
async def strategist(idea: str, audience: str) -> dict:
    system = (
        "You are a startup strategist. Return ONLY JSON with keys "
        '"name", "tagline", "value_proposition". Keep it punchy and modern.'
    )
    user = f'Idea: "{idea}"\nAudience: "{audience}"'
    return await _call_llm(system, user)


async def copywriter(name: str, value_proposition: str) -> dict:
    system = (
        "You are a landing-page copywriter. Return ONLY JSON with keys "
        '"hero_headline", "hero_subtext", "features" (array of 3 objects with '
        '"title" and "desc"), and "cta".'
    )
    user = f'Startup: "{name}"\nValue proposition: "{value_proposition}"'
    return await _call_llm(system, user)


async def brand(name: str, tagline: str) -> dict:
    system = (
        "You are a brand designer. Return ONLY JSON with keys "
        '"palette" (array of exactly 5 hex color strings, nothing else), '
        '"logo_concept", and "font_style". Ensure accessible contrast.'
    )
    user = f'Startup: "{name}"\nTagline: "{tagline}"'
    return await _call_llm(system, user)


async def social(name: str, value_proposition: str) -> dict:
    system = (
        "You are a social media manager. Return ONLY JSON with key "
        '"captions" — an array of exactly 3 launch captions. Each under 280 '
        "characters with 2-3 relevant hashtags."
    )
    user = f'Startup: "{name}"\nValue proposition: "{value_proposition}"'
    return await _call_llm(system, user)


# ---------------------------------------------------------------------------
# Orchestrator — runs the crew in the right order
# ---------------------------------------------------------------------------
async def run_crew(idea: str, audience: str) -> dict:
    """Coordinate the agents and assemble the full startup kit.

    Resilient by design: if one agent fails, the others still return, so the
    demo never shows a blank screen. Any failed section comes back empty and
    the frontend simply skips it.
    """
    if MOCK_MODE:
        return _load_offline_kit(idea)

    # 1. Strategist first — everything else depends on the name.
    try:
        strategy = await strategist(idea, audience)
    except Exception:
        strategy = {"name": "Your Startup", "tagline": "", "value_proposition": ""}

    name = strategy.get("name", "Your Startup")
    tagline = strategy.get("tagline", "")
    value_prop = strategy.get("value_proposition", "")

    # 2. The other three run in parallel once we have the name.
    #    return_exceptions=True means one failure doesn't sink the others.
    copy, branding, socials = await asyncio.gather(
        copywriter(name, value_prop),
        brand(name, tagline),
        social(name, value_prop),
        return_exceptions=True,
    )

    def safe(result):
        return {} if isinstance(result, Exception) else result

    return {
        "strategy": strategy,
        "copy": safe(copy),
        "brand": _clean_palette(safe(branding)),
        "social": safe(socials),
        "mock": False,
        "_engine": {"provider": "AMD GPU (vLLM)", "model": MODEL},
    }
