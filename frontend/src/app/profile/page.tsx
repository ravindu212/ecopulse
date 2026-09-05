"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ApiError, clearAccessToken, getCurrentUser, getProgress, AuthenticatedUser, ProgressData } from "@/lib/api";
import { AuthNav } from "@/components/layout/auth-nav";

export default function ProfilePage() {
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [error, setError] = useState("");

  useEffect(() => { Promise.all([getCurrentUser(), getProgress()]).then(([currentUser, currentProgress]) => { setUser(currentUser); setProgress(currentProgress); }).catch((requestError) => { if (requestError instanceof ApiError && requestError.status === 401) clearAccessToken(); setError("Sign in to view your profile."); }); }, []);

  if (error || !user || !progress) return <main className="min-h-screen bg-[#071A17] px-5 py-6 text-[#F4FFF9] sm:px-8"><div className="mx-auto max-w-6xl"><AuthNav /><section className="mx-auto mt-16 max-w-xl rounded-2xl border border-white/10 bg-[#0E2722] p-6"><h1 className="text-3xl font-semibold">{error || "Loading your profile…"}</h1>{error && <Link className="mt-5 inline-block rounded-lg bg-[#5EE89A] px-4 py-2 font-semibold text-[#071A17]" href="/login">Sign In</Link>}</section></div></main>;
  const stats = [["Total XP", user.xp], ["Current streak", `${user.current_streak} days`], ["Longest streak", `${user.longest_streak} days`], ["Completed actions", progress.summary.completed_actions]];
  return <main className="min-h-screen bg-[#071A17] px-5 py-6 text-[#F4FFF9] sm:px-8"><div className="mx-auto max-w-6xl"><AuthNav /><header className="max-w-3xl py-12 sm:py-16"><p className="text-sm font-semibold tracking-[0.2em] text-[#5EE89A]">ECO PULSE · PROFILE</p><h1 className="mt-4 text-4xl font-bold sm:text-5xl">{user.name}</h1><p className="mt-3 text-lg text-[#A5BBB2]">{user.email}</p></header><section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{stats.map(([label, value]) => <article key={String(label)} className="rounded-2xl border border-white/10 bg-[#0E2722] p-5"><p className="text-sm text-[#A5BBB2]">{label}</p><strong className="mt-2 block text-3xl">{value}</strong></article>)}</section><section className="mt-8 rounded-2xl border border-white/10 bg-[#15332C] p-6"><h2 className="text-2xl font-semibold">Keep building momentum</h2><p className="mt-3 text-[#A5BBB2]">Your completed actions contribute to your Climate Action Score and estimated CO2e avoided.</p><div className="mt-5 flex flex-wrap gap-3"><Link className="rounded-lg bg-[#5EE89A] px-4 py-2 font-semibold text-[#071A17]" href="/progress">View Progress</Link><Link className="rounded-lg border border-white/20 px-4 py-2 font-semibold" href="/assessment">Take Assessment</Link><Link className="rounded-lg border border-white/20 px-4 py-2 font-semibold" href="/actions">Browse Actions</Link></div></section></div></main>;
}
