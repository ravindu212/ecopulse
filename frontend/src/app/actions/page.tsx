"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ApiError, apiFetch } from "@/lib/api";

type Action = { id: string; title: string; category: string; description: string; difficulty: string; impact_level: string; estimated_co2e_kg: string | null; xp_reward: number; recommendation_reason?: string };

const categories = ["", "transport", "energy", "food", "waste"];
const difficulties = ["", "easy", "medium", "hard"];
const impactLevels = ["", "low", "medium", "high"];

export default function ActionsPage() {
  const [actions, setActions] = useState<Action[]>([]);
  const [recommended, setRecommended] = useState<Action[]>([]);
  const [category, setCategory] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [impactLevel, setImpactLevel] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [needsAuth, setNeedsAuth] = useState(false);

  useEffect(() => {
    const query = new URLSearchParams();
    if (category) query.set("category", category);
    if (difficulty) query.set("difficulty", difficulty);
    if (impactLevel) query.set("impact_level", impactLevel);
    apiFetch<Action[]>(`/actions${query.size ? `?${query}` : ""}`).then(setActions).catch((requestError: Error) => setError(requestError.message));
  }, [category, difficulty, impactLevel]);

  useEffect(() => { apiFetch<Action[]>("/actions/recommended").then(setRecommended).catch(() => {}); }, []);

  function handleError(requestError: unknown) {
    if (requestError instanceof ApiError && requestError.status === 401) {
      setNeedsAuth(true);
      setError("Sign in to start or complete climate actions.");
      return;
    }
    setError(requestError instanceof Error ? requestError.message : "Unable to update this action.");
  }

  async function start(id: string) {
    try {
      await apiFetch(`/actions/${id}/start`, { method: "POST" });
      setMessage("Action started — come back when you are ready to complete it.");
    } catch (requestError) { handleError(requestError); }
  }

  async function complete(id: string) {
    try {
      const result = await apiFetch<{ xp_awarded: number; xp: number; current_streak: number }>(`/actions/${id}/complete`, { method: "POST" });
      setMessage(`Completed! +${result.xp_awarded} XP · ${result.current_streak}-day streak · ${result.xp} total XP.`);
    } catch (requestError) { handleError(requestError); }
  }

  return <main className="mx-auto max-w-5xl p-6"><p className="text-sm font-semibold text-emerald-700">ECO PULSE · ACTIONS</p><h1 className="mt-2 text-4xl font-bold">Small actions, real momentum.</h1>{message && <p className="mt-5 rounded bg-emerald-50 p-3 text-emerald-800">{message}</p>}{error && <p className="mt-5 rounded bg-red-50 p-3 text-red-700">{error}{needsAuth && <> <Link className="font-semibold underline" href="/login">Sign in</Link></>}</p>}{recommended.length > 0 && <section className="mt-8"><h2 className="text-2xl font-semibold">Recommended for you</h2><div className="mt-3 grid gap-4 md:grid-cols-3">{recommended.map((action) => <Card key={action.id} action={action} start={start} complete={complete} />)}</div></section>}<section className="mt-10"><div className="flex flex-wrap items-end justify-between gap-4"><h2 className="text-2xl font-semibold">All climate actions</h2><div className="flex flex-wrap gap-3"><Filter label="Category" value={category} values={categories} onChange={setCategory} /><Filter label="Difficulty" value={difficulty} values={difficulties} onChange={setDifficulty} /><Filter label="Impact" value={impactLevel} values={impactLevels} onChange={setImpactLevel} /></div></div>{actions.length ? <div className="mt-3 grid gap-4 md:grid-cols-2">{actions.map((action) => <Card key={action.id} action={action} start={start} complete={complete} />)}</div> : <p className="mt-4 rounded border border-dashed p-4 text-zinc-600">No actions match these filters. Try broadening your selection.</p>}</section></main>;
}

function Filter({ label, value, values, onChange }: { label: string; value: string; values: string[]; onChange: (value: string) => void }) {
  return <label className="text-sm font-medium">{label}<select className="ml-2 rounded border px-2 py-1" value={value} onChange={(event) => onChange(event.target.value)}>{values.map((option) => <option key={option || "all"} value={option}>{option ? option[0].toUpperCase() + option.slice(1) : `All ${label.toLowerCase()}s`}</option>)}</select></label>;
}

function Card({ action, start, complete }: { action: Action; start: (id: string) => void; complete: (id: string) => void }) {
  return <article className="rounded-xl border p-5"><p className="text-sm capitalize text-emerald-700">{action.category} · {action.difficulty}</p><h3 className="mt-1 text-xl font-semibold">{action.title}</h3><p className="mt-2 text-zinc-600">{action.description}</p>{action.recommendation_reason && <p className="mt-3 text-sm text-emerald-800">{action.recommendation_reason}</p>}<p className="mt-4 text-sm">{action.xp_reward} XP · {action.impact_level} impact{action.estimated_co2e_kg ? ` · Estimated CO2e avoided: ${action.estimated_co2e_kg} kg` : ""}</p><button className="mt-4 rounded border px-4 py-2" onClick={() => start(action.id)}>Start</button><button className="mt-4 ml-2 rounded bg-emerald-700 px-4 py-2 text-white" onClick={() => complete(action.id)}>Complete</button></article>;
}
