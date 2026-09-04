"use client";

import Link from "next/link";

type Result = { overall_score: number; lowest_category: string; transport_score: number; energy_score: number; food_score: number; waste_score: number };
export default function ResultsPage() {
  const saved = typeof window === "undefined" ? null : sessionStorage.getItem("ecopulse_assessment_result");
  const result: Result | null = saved ? JSON.parse(saved) : null;
  if (!result) return <main className="p-8">No assessment result is available yet. <Link className="text-emerald-700 underline" href="/assessment">Take the assessment</Link>.</main>;
  const scores = [["Transport", result.transport_score], ["Energy", result.energy_score], ["Food", result.food_score], ["Waste", result.waste_score]];
  return <main className="mx-auto max-w-2xl p-6"><p className="text-sm font-semibold text-emerald-700">YOUR CLIMATE ACTION SCORE</p><h1 className="mt-2 text-6xl font-bold">{result.overall_score}<span className="text-2xl">/100</span></h1><p className="mt-4 text-zinc-600">This lifestyle climate score reflects the habits you shared. It is not an official carbon-footprint calculation.</p><section className="mt-8 rounded-xl border p-5"><h2 className="text-xl font-semibold">Your biggest opportunity</h2><p className="mt-2 capitalize">{result.lowest_category} is currently your lowest-scoring category.</p></section><section className="mt-6 space-y-4">{scores.map(([label, score]) => <div key={String(label)}><div className="flex justify-between"><span>{label}</span><strong>{score}/100</strong></div><div className="mt-1 h-3 rounded bg-zinc-200"><div className="h-3 rounded bg-emerald-600" style={{ width: `${score}%` }} /></div></div>)}</section><Link href="/assessment" className="mt-8 inline-block text-emerald-700 underline">Retake assessment</Link></main>;
}
