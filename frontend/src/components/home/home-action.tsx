import Link from "next/link";
import { ArrowRight, BarChart3, Compass, ListChecks, Sparkles } from "lucide-react";

export function HomeAction() {
  return (
    <>
      <section className="home-human-bridge" data-home-scene data-scene-key="human">
        <div><p className="home-kicker">12 · From observation to agency</p><h2>The global system is larger than any one person.<br /><em>Your next step can still be specific.</em></h2></div>
        <p>Understanding the climate system is one part of climate action. EcoPulse can also help you reflect on everyday habits, find practical options, and keep track of the actions you choose—without pretending personal choices replace systemic change.</p>
      </section>

      <section className="home-pathway" data-home-scene data-scene-key="pathway">
        <div className="home-pathway-copy"><p className="home-kicker">Optional personal climate pathway</p><h2>Personalize EcoPulse when you&apos;re ready.</h2><p>A short educational assessment can identify relevant lifestyle categories, tailor rule-based recommendations, build practical scenarios, and make your own progress visible.</p><p className="home-pathway-note">This pathway does not predict Earth&apos;s climate and is not a certified carbon footprint.</p><div><Link href="/assessment">Build your climate pathway <ArrowRight size={16} aria-hidden="true" /></Link><Link href="/login">Continue to your dashboard</Link></div></div>
        <ol>
          <li><Compass aria-hidden="true" /><span>01</span><strong>Reflect</strong><p>Look across transport, energy, food, and waste.</p></li>
          <li><Sparkles aria-hidden="true" /><span>02</span><strong>Choose</strong><p>Receive transparent, rule-based next steps.</p></li>
          <li><ListChecks aria-hidden="true" /><span>03</span><strong>Act</strong><p>Start practical actions that fit your situation.</p></li>
          <li><BarChart3 aria-hidden="true" /><span>04</span><strong>Track</strong><p>See activity, streaks, XP, and educational estimates.</p></li>
        </ol>
      </section>

      <footer className="home-footer">
        <div><p>EcoPulse · public climate intelligence + optional personal action</p><h2>Observe carefully.<br />Understand honestly.<br />Act practically.</h2></div>
        <nav aria-label="Homepage footer"><Link href="/climate-now">Climate Now</Link><Link href="/sources">Sources &amp; methodology</Link><Link href="/assessment">Personalize EcoPulse</Link><Link href="/login">Sign in</Link></nav>
      </footer>
    </>
  );
}
