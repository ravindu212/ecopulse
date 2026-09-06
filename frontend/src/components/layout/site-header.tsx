"use client";

import { ChevronDown, Menu, X } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, useSyncExternalStore } from "react";

import { clearAccessToken, getAccessToken } from "@/lib/api";
import { ThemeToggle } from "@/components/theme-toggle";

const publicLinks = [
  ["Climate Now", "/climate-now"],
  ["Outlooks", "/outlooks"],
  ["Explore", "/explore"],
  ["Learn", "/learn"],
  ["SDG 13", "/sdg/13"],
  ["Take Action", "/actions"],
] as const;

const appLinks = [
  ["Dashboard", "/dashboard"],
  ["Assessment", "/assessment"],
  ["Actions", "/actions"],
  ["Challenges", "/challenges"],
  ["Progress", "/progress"],
  ["Profile", "/profile"],
] as const;

function isCurrentPath(pathname: string, href: string) {
  return pathname === href || (href !== "/" && pathname.startsWith(`${href}/`));
}

export function SiteHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [accountOpen, setAccountOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const update = () => setScrolled(window.scrollY > 28);

    update();
    window.addEventListener("scroll", update, { passive: true });

    return () => window.removeEventListener("scroll", update);
  }, []);

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

  function closeMenus() {
    setMobileOpen(false);
    setAccountOpen(false);
  }

  function logout() {
    clearAccessToken();
    closeMenus();
    router.replace("/login");
  }

  const navLinkClass = (href: string) =>
    `site-nav-link ${isCurrentPath(pathname, href) ? "site-nav-link-active" : ""}`;

  return (
    <div className="site-header-slot">
      <header className={`site-header ${scrolled ? "site-header-scrolled" : ""}`}>
        <nav className="site-header-inner" aria-label="Primary navigation">
          <Link className="site-wordmark" href="/" onClick={closeMenus} aria-label="EcoPulse home">
            <Image
              className="site-wordmark-logo"
              src="/media/home/logo.png"
              alt="EcoPulse"
              width={2172}
              height={724}
              priority
            />
          </Link>

        <div className="site-nav-desktop">
          {publicLinks.map(([label, href]) => (
            <Link
              key={href}
              href={href}
              className={navLinkClass(href)}
              aria-current={isCurrentPath(pathname, href) ? "page" : undefined}
            >
              {label}
            </Link>
          ))}
        </div>

        <div className="site-header-actions">
          <ThemeToggle />
          {authenticated ? (
            <div className="account-menu-wrap">
              <button
                type="button"
                className="site-account-trigger"
                aria-expanded={accountOpen}
                aria-controls="account-navigation"
                onClick={() => setAccountOpen((open) => !open)}
              >
                My EcoPulse <ChevronDown size={14} aria-hidden="true" />
              </button>
              {accountOpen && (
                <div id="account-navigation" className="site-account-menu">
                  <p className="site-menu-label">Personal workspace</p>
                  {appLinks.map(([label, href]) => (
                    <Link key={href} href={href} className={navLinkClass(href)} onClick={closeMenus}>
                      {label}
                    </Link>
                  ))}
                  <button type="button" className="site-menu-logout" onClick={logout}>
                    Sign out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link className="site-sign-in" href="/login">
              Sign in
            </Link>
          )}
          <button
            type="button"
            className="site-mobile-trigger"
            aria-label={mobileOpen ? "Close navigation" : "Open navigation"}
            aria-expanded={mobileOpen}
            aria-controls="mobile-navigation"
            onClick={() => setMobileOpen((open) => !open)}
          >
            {mobileOpen ? <X size={19} aria-hidden="true" /> : <Menu size={19} aria-hidden="true" />}
          </button>
        </div>

        {mobileOpen && (
          <div id="mobile-navigation" className="site-mobile-menu">
            <p className="site-menu-label">Climate intelligence</p>
            {publicLinks.map(([label, href]) => (
              <Link key={href} href={href} className={navLinkClass(href)} onClick={closeMenus}>
                {label}
              </Link>
            ))}
            <div className="site-mobile-divider" />
            <p className="site-menu-label">{authenticated ? "Personal workspace" : "Personalize EcoPulse"}</p>
            {authenticated ? (
              <>
                {appLinks.map(([label, href]) => (
                  <Link key={href} href={href} className={navLinkClass(href)} onClick={closeMenus}>
                    {label}
                  </Link>
                ))}
                <button type="button" className="site-menu-logout" onClick={logout}>
                  Sign out
                </button>
              </>
            ) : (
              <>
                <Link href="/login" className={navLinkClass("/login")} onClick={closeMenus}>Sign in</Link>
                <Link href="/register" className="site-mobile-cta" onClick={closeMenus}>Build your climate pathway</Link>
              </>
            )}
          </div>
        )}
        </nav>
      </header>
    </div>
  );
}
