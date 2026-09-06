"use client";

import dynamic from "next/dynamic";

const HomeScrollController = dynamic(() => import("./home-scroll-controller"), { ssr: false });

export function HomeMotionLoader() {
  return <HomeScrollController />;
}
