"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  ApiError,
  Challenge,
  ChallengeAction,
  clearAccessToken,
  getAccessToken,
  joinChallenge,
  JoinedChallenge,
  listChallenges,
  listMyChallenges,
} from "@/lib/api";
import { AuthNav } from "@/components/layout/auth-nav";

function progressWidth(progress: number) {
  return Math.min(100, Math.max(0, progress));
}

function RequiredActions({ actions }: { actions: ChallengeAction[] }) {
  if (!actions.length) return <p className="mt-5 text-sm text-[#A5BBB2]">No required actions are listed for this challenge.</p>;

  return (
    <ul className="mt-5 space-y-2" aria-label="Required actions">
      {actions.map((action) => (
        <li key={action.id} className="rounded-xl border border-white/10 bg-black/10 px-3 py-2.5 text-sm">
          <p className="font-medium text-[#F4FFF9]">{action.title}</p>
          <p className="mt-1 capitalize text-[#A5BBB2]">{action.category} · {action.difficulty}</p>
        </li>
      ))}
    </ul>
  );
}

function ProgressBar({ progress }: { progress: number }) {
  const width = progressWidth(progress);
  return (
    <div className="mt-5">
      <div className="flex items-center justify-between gap-3 text-sm">
        <span className="text-[#A5BBB2]">Challenge progress</span>
        <strong className="text-[#F4FFF9]">{progress}%</strong>
      </div>
      <div
        className="mt-2 h-2.5 overflow-hidden rounded-full bg-white/10"
        role="progressbar"
        aria-label="Challenge progress"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={width}
      >
        <div className="h-full rounded-full bg-[#5EE89A] transition-[width] duration-500" style={{ width: `${width}%` }} />
      </div>
    </div>
  );
}

function JoinedCard({ membership, challenge }: { membership: JoinedChallenge; challenge?: Challenge }) {
  const completed = membership.status === "completed";
  return (
    <article className="rounded-2xl border border-white/10 bg-[#0E2722] p-5 shadow-[0_20px_60px_rgba(0,0,0,0.18)]">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold tracking-[0.18em] text-[#62D9FF]">YOUR CHALLENGE</p>
          <h3 className="mt-2 text-2xl font-semibold text-[#F4FFF9]">{membership.title}</h3>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${completed ? "bg-[#5EE89A]/15 text-[#5EE89A]" : "bg-[#62D9FF]/15 text-[#62D9FF]"}`}>
          {completed ? "Completed" : "In progress"}
        </span>
      </div>
      {challenge && <p className="mt-3 text-sm leading-6 text-[#A5BBB2]">{challenge.description}</p>}
      <ProgressBar progress={membership.progress_percent} />
      <p className="mt-3 text-sm text-[#A5BBB2]">
        <strong className="text-[#F4FFF9]">{membership.completed_required_actions} / {membership.total_required_actions}</strong> required actions completed
      </p>
      {completed && membership.completed_at && <p className="mt-3 text-sm text-[#5EE89A]">Completed {new Date(membership.completed_at).toLocaleDateString()}</p>}
      <RequiredActions actions={challenge?.required_actions ?? []} />
      <Link className="mt-5 inline-flex rounded-lg border border-[#62D9FF]/50 px-4 py-2 text-sm font-semibold text-[#62D9FF] transition hover:bg-[#62D9FF]/10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#62D9FF]" href="/actions">
        Go to Actions
      </Link>
    </article>
  );
}

export default function ChallengesPage() {
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [memberships, setMemberships] = useState<JoinedChallenge[]>([]);
  const [loading, setLoading] = useState(true);
  const [joiningId, setJoiningId] = useState<string | null>(null);
  const [authenticated, setAuthenticated] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadChallenges() {
      setLoading(true);
      setError("");
      try {
        const catalog = await listChallenges();
        setChallenges(catalog);
        if (!getAccessToken()) return;

        setAuthenticated(true);
        const joined = await listMyChallenges();
        setMemberships(joined);
      } catch (loadError) {
        if (loadError instanceof ApiError && loadError.status === 401) {
          clearAccessToken();
          setAuthenticated(false);
          setNotice("Your session has ended. Sign in to see and join your challenges.");
        } else {
          setError(loadError instanceof Error ? loadError.message : "Unable to load challenges.");
        }
      } finally {
        setLoading(false);
      }
    }

    void loadChallenges();
  }, []);

  const challengeById = useMemo(() => new Map(challenges.map((challenge) => [challenge.id, challenge])), [challenges]);
  const joinedIds = useMemo(() => new Set(memberships.map((membership) => membership.challenge_id)), [memberships]);
  const available = challenges.filter((challenge) => !joinedIds.has(challenge.id));

  async function handleJoin(challengeId: string) {
    if (joiningId || joinedIds.has(challengeId)) return;
    if (!getAccessToken()) {
      setAuthenticated(false);
      setNotice("Sign in to join a climate challenge.");
      return;
    }

    setJoiningId(challengeId);
    setError("");
    setNotice("");
    try {
      await joinChallenge(challengeId);
      setMemberships(await listMyChallenges());
      setNotice("Challenge joined. Your next small action is ready when you are.");
    } catch (joinError) {
      if (joinError instanceof ApiError && joinError.status === 401) {
        clearAccessToken();
        setAuthenticated(false);
        setNotice("Your session has ended. Please sign in to join a challenge.");
      } else {
        setError(joinError instanceof Error ? joinError.message : "Unable to join this challenge.");
      }
    } finally {
      setJoiningId(null);
    }
  }

  if (loading) return <main className="min-h-screen bg-[#071A17] p-6 text-[#F4FFF9]"><div className="mx-auto max-w-6xl py-16 text-[#A5BBB2]">Loading your climate challenges…</div></main>;

  return (
    <main className="min-h-screen bg-[#071A17] px-5 py-6 text-[#F4FFF9] sm:px-8">
      <div className="mx-auto max-w-6xl">
        <AuthNav />

        <header className="max-w-3xl py-12 sm:py-16">
          <p className="text-sm font-semibold tracking-[0.2em] text-[#5EE89A]">ECO PULSE · CHALLENGES</p>
          <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">Build climate habits, one challenge at a time.</h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-[#A5BBB2]">Choose a focused set of practical actions and watch your progress grow from real completed actions.</p>
        </header>

        {notice && <p className="mb-6 rounded-xl border border-[#5EE89A]/30 bg-[#5EE89A]/10 p-4 text-sm text-[#D8FFE8]" role="status">{notice}</p>}
        {error && <p className="mb-6 rounded-xl border border-red-400/30 bg-red-400/10 p-4 text-sm text-red-100" role="alert">{error}</p>}

        {!authenticated ? (
          <section className="rounded-2xl border border-white/10 bg-[#0E2722] p-6 sm:p-8">
            <p className="text-sm font-semibold tracking-[0.16em] text-[#62D9FF]">YOUR CHALLENGES</p>
            <h2 className="mt-3 text-2xl font-semibold">Sign in to make your progress count.</h2>
            <p className="mt-3 max-w-xl leading-7 text-[#A5BBB2]">You can browse the available challenges below. <Link className="font-semibold text-[#62D9FF] hover:text-[#F4FFF9]" href="/login">Sign in</Link> or <Link className="font-semibold text-[#62D9FF] hover:text-[#F4FFF9]" href="/register">create an account</Link> to join one and track your completed actions.</p>
          </section>
        ) : (
          <section>
            <div className="flex flex-wrap items-end justify-between gap-3"><div><p className="text-sm font-semibold tracking-[0.16em] text-[#62D9FF]">YOUR CHALLENGES</p><h2 className="mt-2 text-3xl font-semibold">My Challenges</h2></div><Link className="text-sm font-semibold text-[#62D9FF] hover:text-[#F4FFF9] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#62D9FF]" href="/actions">Complete actions →</Link></div>
            {memberships.length ? <div className="mt-5 grid gap-5 lg:grid-cols-2">{memberships.map((membership) => <JoinedCard key={membership.challenge_id} membership={membership} challenge={challengeById.get(membership.challenge_id)} />)}</div> : <div className="mt-5 rounded-2xl border border-dashed border-white/20 bg-[#0E2722] p-6 text-[#A5BBB2]">No joined challenges yet. Pick one below to turn your next action into momentum.</div>}
          </section>
        )}

        <section className="mt-14 pb-12">
          <p className="text-sm font-semibold tracking-[0.16em] text-[#5EE89A]">CURATED FOR YOU</p>
          <h2 className="mt-2 text-3xl font-semibold">Available Challenges</h2>
          {available.length ? <div className="mt-5 grid gap-5 lg:grid-cols-2">{available.map((challenge) => <article key={challenge.id} className="rounded-2xl border border-white/10 bg-[#15332C] p-5"><h3 className="text-2xl font-semibold">{challenge.title}</h3><p className="mt-3 leading-7 text-[#A5BBB2]">{challenge.description}</p><RequiredActions actions={challenge.required_actions} /><button type="button" className="mt-5 rounded-lg bg-[#5EE89A] px-4 py-2 font-semibold text-[#071A17] transition hover:bg-[#82f0b0] disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#62D9FF]" onClick={() => void handleJoin(challenge.id)} disabled={!authenticated || joiningId === challenge.id}>{joiningId === challenge.id ? "Joining…" : "Join Challenge"}</button></article>)}</div> : <div className="mt-5 rounded-2xl border border-dashed border-white/20 bg-[#0E2722] p-6 text-[#A5BBB2]">You have joined every available challenge. Nice work—your future self is impressed.</div>}
        </section>
      </div>
    </main>
  );
}
