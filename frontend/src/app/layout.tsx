import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { PageMotion } from "@/components/motion";
import { ThemeProvider } from "@/components/theme-provider";
import { SiteFooter } from "@/components/layout/site-footer";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  applicationName: "EcoPulse",
  title: {
    default: "EcoPulse · Climate intelligence for a changing planet",
    template: "%s · EcoPulse",
  },
  description: "Explore current climate signals, understand Earth systems, and build an optional personal climate action pathway.",
  category: "climate science and education",
  openGraph: {
    type: "website",
    siteName: "EcoPulse",
    title: "EcoPulse · Climate intelligence for a changing planet",
    description: "Current climate intelligence, clear explanations, interactive data, and practical personal action.",
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      data-scroll-behavior="smooth"
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col">
        <a className="skip-link" href="#page-content">Skip to content</a>
        <ThemeProvider><PageMotion>{children}</PageMotion><SiteFooter /></ThemeProvider>
      </body>
    </html>
  );
}
