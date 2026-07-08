"""
AI Launchpad — the agent crew.

Four specialized agents, each a single focused LLM call on Fireworks AI
(which runs open models on AMD GPUs). Every agent is forced to return JSON
so the frontend can render the result reliably.

If FIREWORKS_API_KEY is not set, the module runs in MOCK mode and returns
realistic sample data — so you can build and test the UI before your
hackathon credits go live.
"""

import json
import os
import asyncio

import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FIREWORKS_API_KEY", "").strip()
MODEL = os.getenv("FIREWORKS_MODEL", "accounts/fireworks/models/llama-v3p1-8b-instruct")
BASE_URL = os.getenv("FIREWORKS_BASE_URL", "https://api.fireworks.ai/inference/v1")

# USE_MOCK=true forces sample data even when a key is set (handy before
# your credits go live). Otherwise, mock mode turns on only when no key.
FORCE_MOCK = os.getenv("USE_MOCK", "").strip().lower() in ("1", "true", "yes")
MOCK_MODE = FORCE_MOCK or not API_KEY


# ---------------------------------------------------------------------------
# Core LLM call
# ---------------------------------------------------------------------------
async def _call_llm(system_prompt: str, user_prompt: str) -> dict:
    """Send one prompt to Fireworks and parse the JSON response."""
    if MOCK_MODE:
        # Should never be reached (callers short-circuit to mock), but safe.
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
        # Ask the model to return strict JSON.
        "response_format": {"type": "json_object"},
    }

    # Retry a few times on transient failures (timeouts, rate limits, 5xx)
    # so a single hiccup never breaks a live demo.
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
                await asyncio.sleep(1.5 * (attempt + 1))  # brief backoff

    # All retries failed — surface a clear error to the orchestrator.
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
    if MOCK_MODE:
        return {
            "name": "JobHopper",
            "tagline": "Find your flex job, college student!",
            "value_proposition": "Streamline your job search with tailored "
            "opportunities and flexible hours.",
        }
    system = (
        "You are a startup strategist. Return ONLY JSON with keys "
        '"name", "tagline", "value_proposition". Keep it punchy and modern.'
    )
    user = f'Idea: "{idea}"\nAudience: "{audience}"'
    return await _call_llm(system, user)


async def copywriter(name: str, value_proposition: str) -> dict:
    if MOCK_MODE:
        return {
            "hero_headline": "Find Your Dream Job, Tailored Just For You",
            "hero_subtext": "JobHopper connects you with customized job "
            "opportunities that fit your skills and preferences. Work on your terms.",
            "features": [
                {"title": "Tailored Opportunities", "desc": "Get job listings that "
                 "match your skills and career goals, making your search efficient."},
                {"title": "Flexible Hours", "desc": "Choose when and where you work, "
                 "giving you freedom to balance career and personal life."},
                {"title": "Personalized Recommendations", "desc": "We use AI to "
                 "suggest jobs that align with your career path and interests."},
            ],
            "cta": "Start Your JobHopper Journey Now",
        }
    system = (
        "You are a landing-page copywriter. Return ONLY JSON with keys "
        '"hero_headline", "hero_subtext", "features" (array of 3 objects with '
        '"title" and "desc"), and "cta".'
    )
    user = f'Startup: "{name}"\nValue proposition: "{value_proposition}"'
    return await _call_llm(system, user)


async def brand(name: str, tagline: str) -> dict:
    if MOCK_MODE:
        return {
            "palette": ["#4CAF50", "#2E8B57", "#32CD32", "#98FB98", "#D3D3D3"],
            "logo_concept": "A dynamic arrow pointing upwards with the JobHopper "
            "wordmark — symbolizing movement toward new opportunities.",
            "font_style": "Open Sans, sans-serif — clean, modern, and professional.",
        }
    system = (
        "You are a brand designer. Return ONLY JSON with keys "
        '"palette" (array of 5 hex color strings), "logo_concept", and '
        '"font_style". Ensure accessible contrast.'
    )
    user = f'Startup: "{name}"\nTagline: "{tagline}"'
    return await _call_llm(system, user)


async def social(name: str, value_proposition: str) -> dict:
    if MOCK_MODE:
        return {
            "captions": [
                "Revolutionize your job search with JobHopper! Find tailored "
                "opportunities & work on your terms. #JobHopper #CareerRevolution",
                "Say goodbye to generic job applications. JobHopper helps you find "
                "perfect, flexible roles. Join the revolution today! #JobHopper #FlexibleWork",
                "Streamline your career journey with JobHopper. Tailored "
                "opportunities await. #JobHopper #FindYourPerfectRole",
            ]
        }
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
    # 1. Strategist first — everything else depends on the name.
    try:
        strategy = await strategist(idea, audience)
    except Exception:
        strategy = {
            "name": "Your Startup",
            "tagline": "",
            "value_proposition": "",
        }

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
        "brand": safe(branding),
        "social": safe(socials),
        "mock": MOCK_MODE,
    }
