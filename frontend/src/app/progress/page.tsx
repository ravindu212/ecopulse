"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ApiError, clearAccessToken, getAccessToken, getProgress, ProgressData } from "@/lib/api";
import { AuthNav } from "@/components/layout/auth-nav";

function displayDate(value: string) {
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
}

export default function ProgressPage() {
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [loading, setLoading] = useState(true);
  const [unauthenticated, setUnauthenticated] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadProgress() {
      if (!getAccessToken()) {
        setUnauthenticated(true);
        setLoading(false);
        return;
      }
      try {
        setProgress(await getProgress());
      } catch (requestError) {
        if (requestError instanceof ApiError && requestError.status === 401) {
          clearAccessToken();
          setUnauthenticated(true);
        } else {
          setError("We could not load your progress right now. Please try again.");
        }
      } finally {
        setLoading(false);
      }
    }
    void loadProgress();
  }, []);

  if (loading) return <main className="min-h-screen bg-[#071A17] p-8 text-[#F4FFF9]">Loading your progress…</main>;
  if (unauthenticated) return <main className="min-h-screen bg-[#071A17] px-5 py-6 text-[#F4FFF9] sm:px-8"><div className="mx-auto max-w-6xl"><AuthNav /><section className="mx-auto mt-16 max-w-xl rounded-2xl border border-white/10 bg-[#0E2722] p-6 sm:p-8"><p className="text-sm font-semibold tracking-[0.16em] text-[#62D9FF]">YOUR PROGRESS</p><h1 className="mt-3 text-3xl font-semibold">Sign in to see your progress.</h1><p className="mt-3 leading-7 text-[#A5BBB2]">EcoPulse keeps your completed actions, scores, and estimated impact in your account.</p><Link className="mt-5 inline-block rounded-lg bg-[#5EE89A] px-4 py-2 font-semibold text-[#071A17] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#62D9FF]" href="/login">Sign In</Link></section></div></main>;
  if (error || !progress) return <main className="min-h-screen bg-[#071A17] p-8 text-[#F4FFF9]"><p role="alert">{error || "Progress is unavailable."}</p></main>;

  const chartData = progress.assessment_history.map((assessment) => ({ date: displayDate(assessment.assessment_date), score: assessment.overall_score }));
  const summaryCards = [["Total XP", progress.summary.xp], ["Current Streak", `${progress.summary.current_streak} days`], ["Completed Actions", progress.summary.completed_actions], ["Estimated CO2e avoided", `${progress.summary.estimated_co2e_kg_avoided.toFixed(2)} kg`]];

  return <main className="min-h-screen bg-[#071A17] px-5 py-6 text-[#F4FFF9] sm:px-8"><div className="mx-auto max-w-6xl"><AuthNav /><header className="max-w-3xl py-12 sm:py-16"><p className="text-sm font-semibold tracking-[0.2em] text-[#5EE89A]">ECO PULSE · PROGRESS</p><h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">Your Progress</h1><p className="mt-5 text-lg leading-8 text-[#A5BBB2]">A clear view of the actions you have completed and the estimated impact you have built over time.</p></header><section aria-label="Progress summary" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{summaryCards.map(([label, value]) => <article key={String(label)} className="rounded-2xl border border-white/10 bg-[#0E2722] p-5"><p className="text-sm text-[#A5BBB2]">{label}</p><strong className="mt-2 block text-3xl">{value}</strong>{label === "Current Streak" && <p className="mt-2 text-xs text-[#A5BBB2]">Best: {progress.summary.longest_streak} days</p>}</article>)}</section><section className="mt-12"><p className="text-sm font-semibold tracking-[0.16em] text-[#62D9FF]">BY CATEGORY</p><h2 className="mt-2 text-3xl font-semibold">Category activity</h2><div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{progress.category_activity.map((category) => <article key={category.category} className="rounded-2xl border border-white/10 bg-[#15332C] p-5"><p className="capitalize text-[#A5BBB2]">{category.category}</p><strong className="mt-3 block text-2xl">{category.completed_actions}</strong><p className="text-sm text-[#A5BBB2]">completed actions</p><p className="mt-4 text-sm text-[#5EE89A]">Estimated CO2e avoided: {category.estimated_co2e_kg_avoided.toFixed(2)} kg</p></article>)}</div></section><section className="mt-12 rounded-2xl border border-white/10 bg-[#0E2722] p-5 sm:p-6"><p className="text-sm font-semibold tracking-[0.16em] text-[#5EE89A]">CLIMATE ACTION SCORE</p><h2 className="mt-2 text-3xl font-semibold">Assessment history</h2>{chartData.length ? <><p className="mt-3 text-sm text-[#A5BBB2]">{chartData.length} assessment{chartData.length === 1 ? "" : "s"} recorded. Scores are shown in chronological order.</p><div className="mt-6 h-72" aria-label="Chronological Climate Action Score chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={chartData} margin={{ top: 8, right: 16, left: -20, bottom: 8 }}><CartesianGrid stroke="#ffffff1a" strokeDasharray="3 3" /><XAxis dataKey="date" tick={{ fill: "#A5BBB2", fontSize: 12 }} /><YAxis domain={[0, 100]} tick={{ fill: "#A5BBB2", fontSize: 12 }} /><Tooltip contentStyle={{ background: "#15332C", border: "1px solid rgba(255,255,255,.15)", borderRadius: "12px" }} labelStyle={{ color: "#F4FFF9" }} /><Line type="monotone" dataKey="score" name="Climate Action Score" stroke="#5EE89A" strokeWidth={3} dot={{ r: 4, fill: "#5EE89A" }} activeDot={{ r: 5 }} isAnimationActive={false} /></LineChart></ResponsiveContainer></div></> : <div className="mt-5 rounded-xl border border-dashed border-white/20 p-5 text-[#A5BBB2]">No assessment history yet. <Link className="font-semibold text-[#62D9FF] hover:text-[#F4FFF9]" href="/assessment">Take your first assessment</Link> to start tracking your Climate Action Score.</div>}</section><section className="mt-12 pb-12"><p className="text-sm font-semibold tracking-[0.16em] text-[#62D9FF]">RECENTLY COMPLETED</p><h2 className="mt-2 text-3xl font-semibold">Recent activity</h2>{progress.recent_activity.length ? <div className="mt-5 grid gap-3">{progress.recent_activity.map((activity) => <article key={`${activity.title}-${activity.completed_at}`} className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/10 bg-[#0E2722] p-4"><div><h3 className="font-semibold">{activity.title}</h3><p className="mt-1 text-sm capitalize text-[#A5BBB2]">{activity.category} · completed {displayDate(activity.completed_at)}</p></div><p className="text-right text-sm"><strong className="block text-[#5EE89A]">+{activity.xp_awarded} XP</strong><span className="text-[#A5BBB2]">Estimated CO2e avoided: {activity.estimated_co2e_kg_awarded.toFixed(2)} kg</span></p></article>)}</div> : <div className="mt-5 rounded-xl border border-dashed border-white/20 p-5 text-[#A5BBB2]">No completed actions yet. <Link className="font-semibold text-[#62D9FF] hover:text-[#F4FFF9]" href="/actions">Explore climate actions</Link> to get started.</div>}</section></div></main>;
}
