# Running AI Launchpad on AMD Compute

AI Launchpad's agents run on **AMD compute**. Because the backend talks to any
OpenAI-compatible endpoint (configured by `FIREWORKS_BASE_URL` + `FIREWORKS_MODEL`),
inference can run either on a model you host yourself on the **AMD Developer Cloud**
or on **Fireworks AI** (open models on AMD GPUs) — with no code changes.

> **This project was built and verified on Option A below**: a Qwen2.5-7B-Instruct
> model served with vLLM on an AMD Developer Cloud GPU. The captured results are
> committed in [`launchpad_kit.json`](launchpad_kit.json) and
> [`launchpad_kit_fitpro.json`](launchpad_kit_fitpro.json) — note `"mock": false`
> and the `_engine` field recording the AMD provider and model.

---

## Option A — AMD Developer Cloud (self-hosted model on an AMD GPU) ✅ verified

This runs the agents' model on an AMD GPU you control — the clearest
demonstration of AMD compute usage.

**1. Get access.** Go to **https://notebooks.amd.com/hackathon** (note the
`/hackathon` path) and click **Sign in with AMD SSO (Dev Program)**. You must
belong to a registered team to be allocated a GPU.

**2. Launch the notebook.** On the dashboard, keep the environment set to
**`ROCm 7.2 + vLLM 0.16.0 + PyTorch 2.9`** (vLLM is preinstalled — nothing to
`pip install`) and click **Request Notebook**. You land in JupyterLab on the GPU
pod, at `/workspace`.

**3. Serve the model.** Open a Terminal from the JupyterLab launcher and run:

```bash
vllm serve Qwen/Qwen2.5-7B-Instruct \
  --port 8000 \
  --gpu-memory-utilization 0.9 \
  --max-model-len 8192
```

The first run downloads ~15 GB of weights (a few minutes); later runs are much
faster. The server is ready when the log prints:

```
Starting vLLM API server 0 on http://0.0.0.0:8000
Application startup complete.
```

Leave that terminal running — pressing `Ctrl+C` stops the server. vLLM now
exposes an OpenAI-compatible API at `http://localhost:8000/v1`.

**4a. Run the agent crew directly (quickest check).** Open a **second** terminal,
upload [`launchpad_real.py`](launchpad_real.py) to `/workspace`, and run:

```bash
python launchpad_real.py
python launchpad_real.py "a fitness app that builds personalized workout plans" "busy professionals"
```

It runs all four agents against the AMD-hosted model, prints the full startup kit,
and writes `launchpad_kit.json`. It uses only the Python standard library, so
there is nothing to install.

**4b. Or point the full app at it.** In `backend/.env`:

```
FIREWORKS_API_KEY=EMPTY
FIREWORKS_MODEL=Qwen/Qwen2.5-7B-Instruct
FIREWORKS_BASE_URL=http://<your-amd-cloud-host>:8000/v1
USE_MOCK=false
```

Restart the backend — the four agents now run on the AMD GPU you're hosting.

**Tips**
- GPU time is capped (8 hrs per 24 hrs). When you're done, click
  **Turn-off Session** on the dashboard to stop the clock; the remaining time is
  preserved within the 24-hour window.
- Save work under `/workspace` (persistent). The model cache does not persist
  across pod restarts, so expect a re-download on the next launch.
- Pick a model that fits the GPU (~48 GB here) with room for the KV cache.
  Qwen2.5-7B used ~14.4 GB for weights and left ~27 GB of KV cache.

---

## Option B — Fireworks AI (open models on AMD GPUs)

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

## Why this satisfies the AMD compute requirement

The Unicorn Track requires an application that **uses AMD compute resources**.

- **Self-hosted vLLM** runs the model directly on an **AMD Developer Cloud GPU**
  (ROCm). This is the path this project uses and verifies.
- **Fireworks AI** inference also runs on **AMD GPU** infrastructure.

Either path means every agent in the crew executes on AMD compute. The committed
kit files record which engine produced them, so the claim is checkable rather
than merely asserted.
