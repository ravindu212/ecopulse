"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch, getAccessToken } from "@/lib/api";

type Question = { id: string; category: string; text: string; options: { id: string; label: string }[] };
type Result = { id: string; transport_score: number; energy_score: number; food_score: number; waste_score: number; overall_score: number; lowest_category: string; created_at: string };

export default function AssessmentPage() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const router = useRouter();
  useEffect(() => { apiFetch<Question[]>("/assessment/questions").then(setQuestions).catch((e: Error) => setError(e.message)).finally(() => setLoading(false)); }, []);
  async function submit() {
    if (!getAccessToken()) return setError("Please sign in first to save your assessment.");
    if (Object.keys(answers).length !== questions.length) return setError("Please answer every question before continuing.");
    setSubmitting(true); setError("");
    try { const result = await apiFetch<Result>("/assessment", { method: "POST", body: JSON.stringify({ answers }) }); sessionStorage.setItem("ecopulse_assessment_result", JSON.stringify(result)); router.push("/assessment/results"); }
    catch (e) { setError(e instanceof Error ? e.message : "Unable to submit assessment."); }
    finally { setSubmitting(false); }
  }
  if (loading) return <main className="p-8">Loading your Climate Action Score questions…</main>;
  return <main className="mx-auto max-w-3xl p-6"><p className="text-sm font-semibold text-emerald-700">ECO PULSE · LIFESTYLE CLIMATE SCORE</p><h1 className="mt-2 text-4xl font-bold">Understand your everyday habits.</h1><p className="mt-3 text-zinc-600">This is an educational lifestyle score, not an official carbon-footprint calculation.</p>{questions.map((q) => <section key={q.id} className="mt-8 rounded-xl border p-5"><p className="text-sm uppercase text-emerald-700">{q.category}</p><h2 className="mt-1 text-xl font-semibold">{q.text}</h2><div className="mt-4 grid gap-2">{q.options.map((o) => <label key={o.id} className="cursor-pointer rounded-lg border p-3"><input className="mr-3" type="radio" name={q.id} value={o.id} checked={answers[q.id] === o.id} onChange={() => setAnswers({ ...answers, [q.id]: o.id })} />{o.label}</label>)}</div></section>)}{error && <p className="mt-6 rounded-lg bg-red-50 p-3 text-red-700">{error} {!getAccessToken() && <Link className="font-semibold underline" href="/login">Sign in</Link>}</p>}<button onClick={submit} disabled={submitting} className="mt-8 rounded-lg bg-emerald-700 px-5 py-3 font-semibold text-white disabled:opacity-50">{submitting ? "Calculating…" : "Get my Climate Action Score"}</button></main>;
}
