/**
 * Shows the four-agent crew working, one at a time.
 * `activeStep` (0-4) controls how many agents are done:
 *   - agents before activeStep show a green check
 *   - the agent at activeStep shows a spinner ("working")
 *   - agents after activeStep are dimmed ("waiting")
 * This is the visible "AI agents" theme — judges see the crew, not just output.
 */
const AGENTS = [
  { key: "strategist", name: "Strategist", job: "naming your startup" },
  { key: "copywriter", name: "Copywriter", job: "writing your landing page" },
  { key: "brand", name: "Brand Designer", job: "choosing your colors" },
  { key: "social", name: "Social Manager", job: "crafting your captions" },
];

export default function AgentProgress({ activeStep }) {
  const pct = Math.round((activeStep / AGENTS.length) * 100);

  return (
    <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
      <div className="mb-4 flex items-center justify-between">
        <p className="text-xs uppercase tracking-wider text-sky-400">
          Agent crew at work
        </p>
        <span className="text-xs text-slate-400">{pct}%</span>
      </div>

      {/* Progress bar */}
      <div className="mb-5 h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
        <div
          className="progress-fill h-full rounded-full bg-gradient-to-r from-sky-500 to-indigo-500"
          style={{ width: `${pct}%` }}
        />
      </div>
      <ul className="space-y-3">
        {AGENTS.map((agent, i) => {
          const done = i < activeStep;
          const working = i === activeStep;
          return (
            <li
              key={agent.key}
              className={`flex items-center gap-3 transition-opacity duration-300 ${
                i > activeStep ? "opacity-40" : "opacity-100"
              }`}
            >
              {/* status icon */}
              <span className="flex h-7 w-7 shrink-0 items-center justify-center">
                {done && (
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500 text-slate-950 text-sm font-bold">
                    ✓
                  </span>
                )}
                {working && (
                  <span className="h-5 w-5 animate-spin rounded-full border-2 border-slate-700 border-t-sky-400" />
                )}
                {!done && !working && (
                  <span className="h-3 w-3 rounded-full bg-slate-700" />
                )}
              </span>

              {/* label */}
              <div className="flex-1">
                <span
                  className={`font-medium ${
                    done ? "text-emerald-400" : working ? "text-sky-300" : "text-slate-400"
                  }`}
                >
                  {agent.name}
                </span>
                <span className="text-slate-500">
                  {" "}
                  — {done ? "done" : working ? `${agent.job}…` : "waiting"}
                </span>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
