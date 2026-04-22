import "./globals.css";

import type { Metadata } from "next";
import { Space_Grotesk, Source_Sans_3 } from "next/font/google";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
});

const sourceSans = Source_Sans_3({
  subsets: ["latin"],
  variable: "--font-source-sans",
});

export const metadata: Metadata = {
  title: "UTP Schedule Agent Lab",
  description: "Agent Engineering Lab aplicado a horarios UTP",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es" className={`${spaceGrotesk.variable} ${sourceSans.variable}`}>
      <body>{children}</body>
    </html>
  );
}

