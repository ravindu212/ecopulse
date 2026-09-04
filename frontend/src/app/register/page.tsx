"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, register, setAccessToken } from "@/lib/api";
import { AuthNav } from "@/components/layout/auth-nav";

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalizedName = name.trim();
    const normalizedEmail = email.trim().toLowerCase();
    if (normalizedName.length < 2) return setError("Enter a name with at least 2 characters.");
    if (!/^\S+@\S+\.\S+$/.test(normalizedEmail)) return setError("Enter a valid email address.");
    if (password.length < 8) return setError("Use a password with at least 8 characters.");
    if (password !== confirmation) return setError("Your passwords do not match.");

    setSubmitting(true);
    setError("");
    try {
      const response = await register({ name: normalizedName, email: normalizedEmail, password });
      setAccessToken(response.access_token);
      router.replace("/assessment");
    } catch (registrationError) {
      setError(registrationError instanceof ApiError && registrationError.status === 409 ? "An account with this email already exists. Try signing in instead." : "We could not create your account. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return <main className="min-h-screen bg-[#071A17] px-5 py-6 text-[#F4FFF9] sm:px-8"><div className="mx-auto max-w-6xl"><AuthNav /><section className="mx-auto mt-12 max-w-md rounded-2xl border border-white/10 bg-[#0E2722] p-6 shadow-[0_24px_70px_rgba(0,0,0,0.3)] sm:mt-16 sm:p-8"><p className="text-sm font-semibold tracking-[0.18em] text-[#5EE89A]">START YOUR JOURNEY</p><h1 className="mt-3 text-3xl font-bold">Create your EcoPulse account</h1><p className="mt-3 text-[#A5BBB2]">A few small details, then your first Climate Action Score.</p><form className="mt-7 space-y-5" onSubmit={submit} noValidate><label className="block text-sm font-medium" htmlFor="name">Name<input id="name" className="mt-2 w-full rounded-lg border border-white/15 bg-[#071A17] px-3 py-2.5 text-[#F4FFF9] outline-none focus:border-[#62D9FF] focus:ring-2 focus:ring-[#62D9FF]/30" type="text" autoComplete="name" value={name} onChange={(event) => setName(event.target.value)} /></label><label className="block text-sm font-medium" htmlFor="email">Email<input id="email" className="mt-2 w-full rounded-lg border border-white/15 bg-[#071A17] px-3 py-2.5 text-[#F4FFF9] outline-none focus:border-[#62D9FF] focus:ring-2 focus:ring-[#62D9FF]/30" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} /></label><label className="block text-sm font-medium" htmlFor="password">Password<input id="password" className="mt-2 w-full rounded-lg border border-white/15 bg-[#071A17] px-3 py-2.5 text-[#F4FFF9] outline-none focus:border-[#62D9FF] focus:ring-2 focus:ring-[#62D9FF]/30" type="password" autoComplete="new-password" value={password} onChange={(event) => setPassword(event.target.value)} /></label><label className="block text-sm font-medium" htmlFor="confirmation">Confirm password<input id="confirmation" className="mt-2 w-full rounded-lg border border-white/15 bg-[#071A17] px-3 py-2.5 text-[#F4FFF9] outline-none focus:border-[#62D9FF] focus:ring-2 focus:ring-[#62D9FF]/30" type="password" autoComplete="new-password" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} /></label>{error && <p className="rounded-lg border border-red-400/30 bg-red-400/10 p-3 text-sm text-red-100" role="alert">{error}</p>}<button className="w-full rounded-lg bg-[#5EE89A] px-4 py-3 font-semibold text-[#071A17] transition hover:bg-[#82f0b0] disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#62D9FF]" type="submit" disabled={submitting}>{submitting ? "Creating account…" : "Create account"}</button></form><p className="mt-6 text-sm text-[#A5BBB2]">Already have an account? <Link className="font-semibold text-[#62D9FF] hover:text-[#F4FFF9] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#62D9FF]" href="/login">Sign in</Link></p></section></div></main>;
}
