"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useSyncExternalStore } from "react";
import { clearAccessToken, getAccessToken } from "@/lib/api";

const appLinks = [
  ["Dashboard", "/dashboard"],
  ["Assessment", "/assessment"],
  ["Actions", "/actions"],
  ["Challenges", "/challenges"],
] as const;

export function AuthNav() {
  const pathname = usePathname();
  const router = useRouter();
  const authenticated = useSyncExternalStore(
    (notify) => {
      window.addEventListener("storage", notify);
      window.addEventListener("ecopulse-auth", notify);
      return () => {
        window.removeEventListener("storage", notify);
        window.removeEventListener("ecopulse-auth", notify);
      };
    },
    () => Boolean(getAccessToken()),
    () => false,
  );

  function logout() {
    clearAccessToken();
    router.replace("/login");
  }

  return (
    <nav className="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm" aria-label="Primary navigation">
      <Link className="font-semibold tracking-[0.16em] text-[#5EE89A] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#62D9FF]" href="/">
        ECO PULSE
      </Link>
      <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-[#A5BBB2]">
        {authenticated ? appLinks.map(([label, href]) => <Link key={href} className={pathname === href ? "font-semibold text-[#F4FFF9]" : "transition hover:text-[#F4FFF9] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#62D9FF]"} href={href}>{label}</Link>) : <><Link className="transition hover:text-[#F4FFF9] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#62D9FF]" href="/login">Sign In</Link><Link className="transition hover:text-[#F4FFF9] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#62D9FF]" href="/register">Register</Link></>}
      </div>
      {authenticated && <button type="button" className="ml-auto rounded-md border border-white/20 px-3 py-1.5 font-semibold text-[#F4FFF9] transition hover:bg-white/10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#62D9FF]" onClick={logout}>Logout</button>}
    </nav>
  );
}
