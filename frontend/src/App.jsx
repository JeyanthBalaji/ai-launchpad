import { useState, useEffect } from "react";
import ResultKit from "./components/ResultKit.jsx";
import AgentProgress from "./components/AgentProgress.jsx";

// How long each agent visibly "works" before the next lights up (ms).
const STEP_MS = 1100;

// Clickable example ideas — make the demo flow instantly and show variety.
const EXAMPLES = [
  { label: "Coffee subscription", idea: "a monthly coffee bean subscription for home baristas", audience: "coffee lovers" },
  { label: "Fitness app", idea: "a fitness app that builds personalized workout plans", audience: "busy professionals" },
  { label: "Student jobs", idea: "an app that helps students find part-time jobs", audience: "college students" },
  { label: "Pet care", idea: "an on-demand pet care and dog walking service", audience: "pet owners" },
];

// Rotating placeholder ideas so the page feels alive on load.
const PLACEHOLDERS = [
  "an app that helps students find part-time jobs",
  "a monthly specialty coffee subscription",
  "an AI tutor for high-school math",
  "a marketplace for local handmade crafts",
];

export default function App() {
  const [idea, setIdea] = useState("");
  const [audience, setAudience] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [placeholderIdx, setPlaceholderIdx] = useState(0);

  // Rotate the placeholder text every few seconds when the box is empty.
  useEffect(() => {
    if (idea) return;
    const t = setInterval(
      () => setPlaceholderIdx((i) => (i + 1) % PLACEHOLDERS.length),
      2600
    );
    return () => clearInterval(t);
  }, [idea]);

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  function useExample(ex) {
    setIdea(ex.idea);
    setAudience(ex.audience);
  }

  async function handleGenerate(e) {
    e.preventDefault();
    if (!idea.trim()) return;

    setLoading(true);
    setResult(null);
    setError("");
    setActiveStep(0);

    try {
      const fetchPromise = fetch("/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idea, audience: audience || "general" }),
      }).then((r) => {
        if (!r.ok) throw new Error(`Server error (${r.status})`);
        return r.json();
      });

      // Step the crew: Strategist -> Copywriter -> Brand -> Social.
      for (let step = 1; step <= 4; step++) {
        await sleep(STEP_MS);
        setActiveStep(step);
      }

      const data = await fetchPromise;
      await sleep(400);
      setResult(data);
    } catch (err) {
      setError(
        "Could not reach the AI Launchpad API. Make sure the backend is " +
          "running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setResult(null);
    setError("");
    setIdea("");
    setAudience("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-950 text-slate-100">
      {/* Animated background orbs */}
      <div className="orb orb-1" />
      <div className="orb orb-2" />

      <div className="relative z-10 mx-auto max-w-3xl px-6 py-14">
        {/* Header */}
        <header className="text-center">
          {/* Credibility badge */}
          <div className="mx-auto mb-5 inline-flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/70 px-4 py-1.5 text-xs text-slate-300">
            <span className="pulse-dot h-2 w-2 rounded-full bg-emerald-400" />
            Powered by AMD Developer Cloud GPUs · vLLM
          </div>

          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
            AI <span className="animated-gradient">Launchpad</span>
          </h1>
          <p className="mt-3 text-lg text-slate-400">
            Turn one idea into a full startup kit in seconds.
          </p>
        </header>

        {/* Input form */}
        <form
          onSubmit={handleGenerate}
          className="mt-9 rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl shadow-black/20"
        >
          <label className="block text-sm font-medium text-slate-300">
            Your idea
          </label>
          <input
            type="text"
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            placeholder={PLACEHOLDERS[placeholderIdx]}
            className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 placeholder-slate-500 transition focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/20"
          />

          {/* Example chips */}
          <div className="mt-3 flex flex-wrap gap-2">
            <span className="py-1 text-xs text-slate-500">Try:</span>
            {EXAMPLES.map((ex) => (
              <button
                key={ex.label}
                type="button"
                onClick={() => useExample(ex)}
                className="rounded-full border border-slate-700 bg-slate-800/50 px-3 py-1 text-xs text-slate-300 transition hover:border-sky-500 hover:text-sky-300"
              >
                {ex.label}
              </button>
            ))}
          </div>

          <label className="mt-5 block text-sm font-medium text-slate-300">
            Audience <span className="text-slate-500">(optional)</span>
          </label>
          <input
            type="text"
            value={audience}
            onChange={(e) => setAudience(e.target.value)}
            placeholder="college students"
            className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 placeholder-slate-500 transition focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/20"
          />

          <button
            type="submit"
            disabled={loading || !idea.trim()}
            className="mt-6 w-full rounded-lg bg-sky-500 px-4 py-3 font-semibold text-slate-950 transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Generating…" : "Launch it 🚀"}
          </button>
        </form>

        {/* Live agent crew */}
        {loading && <AgentProgress activeStep={activeStep} />}

        {/* Error */}
        {error && (
          <div className="mt-8 rounded-lg border border-red-800 bg-red-950/50 p-4 text-red-300">
            {error}
          </div>
        )}

        {/* Results */}
        {result && !loading && <ResultKit data={result} onReset={reset} />}

        {/* Footer */}
        <footer className="mt-16 text-center text-xs text-slate-600">
          AI Launchpad · A crew of AI agents on AMD GPUs · AMD Developer Hackathon: ACT II
        </footer>
      </div>
    </div>
  );
}
