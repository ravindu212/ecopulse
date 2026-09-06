import Link from "next/link";
import Image from "next/image";

export function SiteFooter() {
  return <footer className="site-footer">
    <div className="site-footer-inner">
      <div className="site-footer-intro">
          <Link className="site-wordmark" href="/" aria-label="EcoPulse home">
            <Image
              className="site-wordmark-logo"
              src="/media/home/logo.png"
              alt="EcoPulse"
              width={2172}
              height={724}
              priority
            />
          </Link>
        <strong>Climate signals, understood.</strong>
        <p>Authoritative climate data translated into clear public intelligence.</p>
        </div>
        <nav aria-label="Explore EcoPulse"><p>Explore</p><Link href="/climate-now">Climate Now</Link><Link href="/indicators">Indicators</Link><Link href="/outlooks">Outlooks</Link><Link href="/events">Earth Events</Link><Link href="/explore">Explore</Link></nav><nav aria-label="Understand EcoPulse"><p>Understand</p><Link href="/learn">Learn</Link><Link href="/sdg/13">SDG 13</Link><Link href="/sources">Sources</Link></nav><div className="site-footer-principles"><p>Data principles</p><span>Observation ≠ forecast</span><span>Detection ≠ attribution</span><span>Personal action ≠ climate prediction</span></div></div><div className="site-footer-bottom"><span>EcoPulse · SDG 13 · Climate Action</span><span>NOAA · NASA · WMO · Copernicus</span></div></footer>;
}
