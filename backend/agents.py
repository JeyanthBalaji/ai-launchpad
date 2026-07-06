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

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{BASE_URL}/chat/completions", headers=headers, json=payload
        )
        resp.raise_for_status()
        data = resp.json()

    content = data["choices"][0]["message"]["content"]
    return _safe_json(content)


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
            "name": "JobSpring",
            "tagline": "Your next shift, one tap away.",
            "value_proposition": "JobSpring connects students with flexible, "
            "verified part-time jobs near campus in seconds.",
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
            "hero_headline": "Find part-time work that fits your schedule",
            "hero_subtext": "Verified local jobs, flexible hours, instant apply — "
            "built for students.",
            "features": [
                {"title": "Verified jobs", "desc": "Every listing is checked so you "
                 "only see real, safe opportunities."},
                {"title": "Flexible hours", "desc": "Filter by shifts that fit "
                 "around your classes."},
                {"title": "Instant apply", "desc": "One tap to apply — no long forms, "
                 "no waiting."},
            ],
            "cta": "Find your first shift",
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
            "palette": ["#0F172A", "#2563EB", "#38BDF8", "#F8FAFC", "#F59E0B"],
            "logo_concept": "A stylized sprouting leaf inside a location pin — "
            "growth plus 'jobs near you'.",
            "font_style": "Geometric sans-serif (e.g. Poppins) — friendly and modern.",
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
                "Class in the morning, shift in the afternoon. JobSpring finds "
                "part-time work that fits your life. #StudentJobs #SideHustle",
                "Stop scrolling sketchy listings. Every JobSpring job is verified "
                "and near your campus. #PartTime #StudentLife",
                "Your schedule is busy enough. Let JobSpring find the shift — you "
                "just show up. #Students #Flexible",
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
    """Coordinate the agents and assemble the full startup kit."""
    # 1. Strategist first — everything else depends on the name.
    strategy = await strategist(idea, audience)
    name = strategy.get("name", "Your Startup")
    tagline = strategy.get("tagline", "")
    value_prop = strategy.get("value_proposition", "")

    # 2. The other three can run in parallel once we have the name.
    copy, branding, socials = await asyncio.gather(
        copywriter(name, value_prop),
        brand(name, tagline),
        social(name, value_prop),
    )

    return {
        "strategy": strategy,
        "copy": copy,
        "brand": branding,
        "social": socials,
        "mock": MOCK_MODE,
    }
