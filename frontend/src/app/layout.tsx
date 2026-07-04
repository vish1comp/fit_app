import type { Metadata } from "next";
import "./globals.css";
import Providers from "../components/Providers";

export const metadata: Metadata = {
  title: "FitSphere AI - Next Gen Fitness & Nutrition SaaS",
  description: "AI-Powered personalized diet and workout coach with progress logs, scientific supplement information and professional tracker logs.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased selection:bg-indigo-500/30">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
