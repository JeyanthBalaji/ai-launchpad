# Running AI Launchpad on AMD Compute

AI Launchpad's agents run on **AMD compute**. Because the backend talks to any
OpenAI-compatible endpoint (configured by `FIREWORKS_BASE_URL` + `FIREWORKS_MODEL`),
you can run inference either on **Fireworks AI** (open models on AMD GPUs) or on a
model you host yourself on the **AMD Developer Cloud** — with no code changes.

---

## Option A — Fireworks AI (open models on AMD GPUs)

Fireworks serves open models on AMD GPU infrastructure. During the hackathon you
receive a Fireworks API key + credits (an email with a code, one per team).

In `backend/.env`:

```
FIREWORKS_API_KEY=fw_xxxxxxxxxxxxxxxx
FIREWORKS_MODEL=accounts/fireworks/models/minimax-m3   # or a Kimi K model
FIREWORKS_BASE_URL=https://api.fireworks.ai/inference/v1
USE_MOCK=false
```

Restart the backend — every agent call now runs on AMD GPUs via Fireworks.

---

## Option B — AMD Developer Cloud (self-hosted model on an AMD GPU)

This runs the agents' model on an AMD GPU instance you control — the clearest
demonstration of AMD compute usage.

**1. Get access.** Go to **https://notebooks.amd.com/hackathon** (note the
`/hackathon` path), sign in with the AMD Developer Program, and open your team's
GPU instance (≈48 GB GPU memory; persistent storage at `/workspace`).

**2. Serve a model with vLLM.** In a terminal in your Jupyter pod:

```bash
pip install vllm
vllm serve Qwen/Qwen2-7B-Instruct --port 8000 --gpu-memory-utilization 0.3
```

vLLM exposes an OpenAI-compatible API at `http://<host>:8000/v1`.

**3. Point AI Launchpad at it.** In `backend/.env`:

```
FIREWORKS_API_KEY=EMPTY
FIREWORKS_MODEL=Qwen/Qwen2-7B-Instruct
FIREWORKS_BASE_URL=http://<your-amd-cloud-host>:8000/v1
USE_MOCK=false
```

Restart the backend — the four agents now run on the AMD GPU you're hosting.

**Tips**
- Save work under `/workspace` (persistent, 25 GB). Stop/restart the pod to
  conserve your compute-hours quota.
- Pick a model that fits in ~48 GB (leaving room for the KV cache).

---

## Why this satisfies the AMD compute requirement

- **Fireworks AI** inference runs on **AMD GPU** infrastructure.
- **Self-hosted vLLM** runs directly on an **AMD Developer Cloud GPU** instance.

Either path means every agent in the crew executes on AMD compute — which the
Unicorn Track requires.
