import Link from "next/link";

import { SiteHeader } from "@/components/layout/site-header";

type PublicPageFoundationProps = {
  eyebrow: string;
  title: string;
  description: string;
  questions: readonly string[];
};

export function PublicPageFoundation({ eyebrow, title, description, questions }: PublicPageFoundationProps) {
  return (
    <main className="min-h-screen bg-[var(--background)] px-5 py-6 text-[var(--foreground)] sm:px-[4vw]">
      <div className="mx-auto max-w-[100rem]">
        <SiteHeader />
        <section className="grid min-h-[70vh] content-between gap-16 py-16 sm:py-24 lg:grid-cols-[1fr_22rem] lg:items-end">
          <div className="max-w-3xl">
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] text-[var(--secondary)]">{eyebrow}</p>
            <h1 className="mt-5 text-5xl font-semibold leading-[0.96] tracking-[-0.055em] text-[var(--foreground-strong)] sm:text-7xl">{title}</h1>
            <p className="mt-7 max-w-2xl text-lg leading-8 text-[var(--muted)] sm:text-xl">{description}</p>
            <p className="mt-8 max-w-xl border-l-2 border-[var(--primary)] pl-4 text-sm leading-6 text-[var(--muted)]">
              Source-backed climate modules are not available here yet. EcoPulse will never substitute an unsourced value; verified feeds and issued bulletins will appear with freshness and methodology notes.
            </p>
          </div>
          <aside className="border-t border-[var(--border)] pt-5 lg:border-l lg:border-t-0 lg:pl-6 lg:pt-0">
            <p className="font-mono text-xs uppercase tracking-[0.16em] text-[var(--muted)]">This page will answer</p>
            <ol className="mt-5 space-y-4">
              {questions.map((question, index) => (
                <li key={question} className="grid grid-cols-[1.8rem_1fr] gap-2 text-sm leading-6">
                  <span className="font-mono text-[var(--primary)]">0{index + 1}</span>
                  <span>{question}</span>
                </li>
              ))}
            </ol>
          </aside>
        </section>
        <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-[var(--border)] py-7 text-sm text-[var(--muted)]">
          <p>EcoPulse climate intelligence and personal action.</p>
          <Link className="font-semibold text-[var(--foreground)]" href="/">Return to the overview</Link>
        </footer>
      </div>
    </main>
  );
}
