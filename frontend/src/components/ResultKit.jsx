import { useState } from "react";
import { downloadKit } from "../kit.js";

/**
 * Renders the full startup kit with a dramatic staggered reveal:
 * identity -> live landing page -> brand -> social, each sliding in after
 * the previous. Interactive touches: copy captions, hover-to-copy palette.
 */
export default function ResultKit({ data, onReset }) {
  const { strategy = {}, copy = {}, brand = {}, social = {}, mock } = data;
  const palette = brand.palette || [];
  const primary = palette[1] || "#2563EB";
  const dark = palette[0] || "#0F172A";
  const initial = (strategy.name || "?").trim().charAt(0).toUpperCase();

  const [copied, setCopied] = useState(null);

  function copyText(text, id) {
    navigator.clipboard?.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied((c) => (c === id ? null : c)), 1400);
  }

  return (
    <div className="mt-10 space-y-8">
      {mock && (
        <div className="animate-reveal rounded-lg border border-amber-800 bg-amber-950/40 p-3 text-sm text-amber-300">
          Running in <strong>mock mode</strong> (sample data). Add your Fireworks
          key and set <code>USE_MOCK=false</code> for live AI output.
        </div>
      )}

      {/* Strategy card */}
      <section
        className="animate-reveal rounded-2xl border border-slate-800 bg-slate-900/60 p-6"
        style={{ animationDelay: "0.05s" }}
      >
        <p className="text-xs uppercase tracking-wider text-sky-400">
          Startup identity
        </p>
        <div className="mt-2 flex items-center gap-4">
          {/* Animated logo mark — styled circle with the startup's initial */}
          <div
            className="animate-pop flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl text-2xl font-bold text-white shadow-lg"
            style={{
              background: `linear-gradient(135deg, ${palette[1] || "#2563EB"}, ${
                palette[2] || "#38BDF8"
              })`,
            }}
          >
            {initial}
          </div>
          <div>
            <h2 className="text-3xl font-bold">{strategy.name}</h2>
            <p className="text-lg text-slate-300">{strategy.tagline}</p>
          </div>
        </div>
        <p className="mt-3 text-slate-400">{strategy.value_proposition}</p>
      </section>

      {/* Live landing-page preview */}
      <section
        className="animate-reveal overflow-hidden rounded-2xl border border-slate-800"
        style={{ animationDelay: "0.2s" }}
      >
        <div className="flex items-center justify-between px-6 py-3 text-xs uppercase tracking-wider text-slate-400 bg-slate-900/60">
          <span>Live landing page preview</span>
          <span className="flex gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-slate-700" />
            <span className="h-2.5 w-2.5 rounded-full bg-slate-700" />
            <span className="h-2.5 w-2.5 rounded-full bg-slate-700" />
          </span>
        </div>
        <div style={{ background: dark }} className="px-8 py-12 text-center">
          <h3 className="text-3xl font-bold text-white">{copy.hero_headline}</h3>
          <p className="mx-auto mt-3 max-w-lg text-slate-300">
            {copy.hero_subtext}
          </p>
          <button
            className="mt-6 rounded-lg px-6 py-3 font-semibold text-white transition hover:opacity-90"
            style={{ background: primary }}
          >
            {copy.cta}
          </button>

          <div className="mt-10 grid gap-4 sm:grid-cols-3 text-left">
            {(copy.features || []).map((f, i) => (
              <div
                key={i}
                className="rounded-xl bg-white/5 p-4 backdrop-blur transition hover:bg-white/10"
              >
                <h4 className="font-semibold text-white">{f.title}</h4>
                <p className="mt-1 text-sm text-slate-300">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Brand */}
      <section
        className="animate-reveal rounded-2xl border border-slate-800 bg-slate-900/60 p-6"
        style={{ animationDelay: "0.35s" }}
      >
        <p className="text-xs uppercase tracking-wider text-sky-400">Brand</p>
        <div className="mt-3 flex flex-wrap gap-3">
          {palette.map((c, i) => (
            <button
              key={i}
              type="button"
              onClick={() => copyText(c, `color-${i}`)}
              className="group text-center focus:outline-none"
              title="Click to copy"
            >
              <div
                className="h-14 w-14 rounded-lg border border-slate-700 transition group-hover:scale-105"
                style={{ background: c }}
              />
              <span className="mt-1 block text-xs text-slate-400 group-hover:text-sky-300">
                {copied === `color-${i}` ? "copied!" : c}
              </span>
            </button>
          ))}
        </div>
        {brand.logo_concept && (
          <p className="mt-4 text-sm text-slate-400">
            <span className="text-slate-300">Logo concept: </span>
            {brand.logo_concept}
          </p>
        )}
        {brand.font_style && (
          <p className="mt-1 text-sm text-slate-400">
            <span className="text-slate-300">Font: </span>
            {brand.font_style}
          </p>
        )}
      </section>

      {/* Social */}
      <section
        className="animate-reveal rounded-2xl border border-slate-800 bg-slate-900/60 p-6"
        style={{ animationDelay: "0.5s" }}
      >
        <p className="text-xs uppercase tracking-wider text-sky-400">
          Social captions
        </p>
        <ul className="mt-3 space-y-3">
          {(social.captions || []).map((cap, i) => (
            <li
              key={i}
              className="flex items-start justify-between gap-3 rounded-lg border border-slate-800 bg-slate-950 p-3 text-sm text-slate-300"
            >
              <span>{cap}</span>
              <button
                type="button"
                onClick={() => copyText(cap, `cap-${i}`)}
                className="shrink-0 rounded-md border border-slate-700 px-2 py-1 text-xs text-slate-400 transition hover:border-sky-500 hover:text-sky-300"
              >
                {copied === `cap-${i}` ? "Copied" : "Copy"}
              </button>
            </li>
          ))}
        </ul>
      </section>

      {/* Actions */}
      <div
        className="animate-reveal flex flex-wrap justify-center gap-3 pt-2"
        style={{ animationDelay: "0.6s" }}
      >
        <button
          type="button"
          onClick={() => downloadKit(data)}
          className="rounded-lg bg-sky-500 px-6 py-3 font-semibold text-slate-950 transition hover:bg-sky-400"
        >
          ⬇ Download kit
        </button>
        <button
          type="button"
          onClick={onReset}
          className="rounded-lg border border-slate-700 bg-slate-900 px-6 py-3 font-medium text-slate-200 transition hover:border-sky-500 hover:text-sky-300"
        >
          ↻ Try another idea
        </button>
      </div>
    </div>
  );
}
