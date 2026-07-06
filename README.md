# AI Launchpad 🚀

**Turn one idea into a full startup kit in seconds.**

Type one line about a business idea and a crew of AI agents instantly generates
a startup name, a ready landing page, a brand look, and social captions — all
running on **AMD GPUs via Fireworks AI**.

Built for the **AMD Developer Hackathon: ACT II** (Unicorn Track).

---

## What it does

You enter an idea like *"an app that helps students find part-time jobs."*
Four agents run:

| Agent | Output |
|-------|--------|
| Strategist | name, tagline, value proposition |
| Copywriter | landing-page copy (hero, 3 features, CTA) |
| Brand | 5-color palette, logo concept, font style |
| Social | 3 launch captions |

The app renders it live as a startup kit — including a working landing-page
preview.

---

## Tech stack

- **Frontend:** React + Vite + Tailwind CSS
- **Backend:** Python + FastAPI
- **AI:** Fireworks AI (open models on AMD GPUs), one focused call per agent
- **Packaging:** Docker + docker-compose

---

## Run it locally (development)

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then add your Fireworks key (optional for mock mode)
uvicorn main:app --reload --port 8000
```

The API runs at http://localhost:8000. Without a key it runs in **mock mode**
and returns sample data, so you can build the UI right away.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

---

## Run it with Docker (production-style)

```bash
# from the project root, with backend/.env filled in
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend:  http://localhost:8000

---

## Get your Fireworks API key

At hackathon kickoff you receive Fireworks AI credits. Create an API key in the
Fireworks dashboard, then put it in `backend/.env`:

```
FIREWORKS_API_KEY=fw_xxxxxxxxxxxxxxxx
```

Restart the backend and it switches from mock mode to real AI output.

---

## Project structure

```
AI launchpad/
├── backend/
│   ├── main.py            FastAPI app + /generate route
│   ├── agents.py          the 4-agent crew + orchestrator
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx        input form + reveal
│   │   └── components/ResultKit.jsx   renders the startup kit
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── agent-prompts.md
```

---

## Deploy on AMD Developer Cloud

Build the images and run the same `docker compose up` on your AMD Developer
Cloud instance using your hackathon credits.
