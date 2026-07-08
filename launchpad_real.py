#!/usr/bin/env python3
"""
AI Launchpad - real inference runner (AMD Developer Cloud).

Runs the four-agent crew against a local vLLM OpenAI-compatible server
(default http://localhost:8000/v1) and prints + saves a full startup kit.
Uses ONLY the Python standard library, so it runs anywhere with no installs.

Usage:
    python launchpad_real.py
    python launchpad_real.py "an app that helps students find part-time jobs" "college students"
"""
import json
import os
import sys
import urllib.request

BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:8000/v1")
MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-7B-Instruct")


def _safe_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end + 1])
        raise


def call_llm(system, user):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.7,
        "max_tokens": 800,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer EMPTY"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode())
    return _safe_json(data["choices"][0]["message"]["content"])


# --- The four agents (same prompts as backend/agents.py) --------------------
def strategist(idea, audience):
    system = ('You are a startup strategist. Return ONLY JSON with keys '
              '"name", "tagline", "value_proposition". Keep it punchy and modern.')
    return call_llm(system, f'Idea: "{idea}"\nAudience: "{audience}"')


def copywriter(name, vp):
    system = ('You are a landing-page copywriter. Return ONLY JSON with keys '
              '"hero_headline", "hero_subtext", "features" (array of 3 objects '
              'with "title" and "desc"), and "cta".')
    return call_llm(system, f'Startup: "{name}"\nValue proposition: "{vp}"')


def brand(name, tagline):
    system = ('You are a brand designer. Return ONLY JSON with keys '
              '"palette" (array of 5 hex color strings), "logo_concept", and '
              '"font_style". Ensure accessible contrast.')
    return call_llm(system, f'Startup: "{name}"\nTagline: "{tagline}"')


def social(name, vp):
    system = ('You are a social media manager. Return ONLY JSON with key '
              '"captions" - an array of exactly 3 launch captions. Each under '
              '280 characters with 2-3 relevant hashtags.')
    return call_llm(system, f'Startup: "{name}"\nValue proposition: "{vp}"')


def safe_call(label, fn, *args):
    try:
        print(f"  {label} ...", flush=True)
        return fn(*args)
    except Exception as ex:  # resilient: one failure never sinks the run
        print(f"  ! {label} failed: {ex}", flush=True)
        return {}


def main():
    idea = sys.argv[1] if len(sys.argv) > 1 else \
        "an app that helps students find part-time jobs"
    audience = sys.argv[2] if len(sys.argv) > 2 else "college students"

    print("\n" + "=" * 62)
    print(" AI Launchpad - running on AMD GPU")
    print(f" Engine : vLLM  |  Model: {MODEL}")
    print(f" Idea   : {idea}")
    print(f" Audience: {audience}")
    print("=" * 62 + "\n")

    strategy = safe_call("[1/4] Strategist", strategist, idea, audience)
    name = strategy.get("name", "Your Startup")
    tagline = strategy.get("tagline", "")
    vp = strategy.get("value_proposition", "")
    print(f"        -> {name} - {tagline}\n")

    copy = safe_call("[2/4] Copywriter", copywriter, name, vp)
    branding = safe_call("[3/4] Brand designer", brand, name, tagline)
    socials = safe_call("[4/4] Social manager", social, name, vp)

    kit = {
        "strategy": strategy,
        "copy": copy,
        "brand": branding,
        "social": socials,
        "mock": False,
        "_engine": {"provider": "AMD Developer Cloud (vLLM)", "model": MODEL},
    }

    print("\n" + "=" * 62)
    print(" FULL STARTUP KIT  (generated on AMD compute)")
    print("=" * 62)
    print(json.dumps(kit, indent=2, ensure_ascii=False))

    out = os.getenv("KIT_OUT", "launchpad_kit.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(kit, f, indent=2, ensure_ascii=False)
    print(f"\nSaved full kit to: {out}\n")


if __name__ == "__main__":
    main()
