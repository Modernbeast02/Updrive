import Image from "next/image";
import localFont from "next/font/local";
import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export default function Home() {
  return (
    <>
      <div className="h-screen w-screen bg-gray-900">
        <Navbar />
        <section className="bg-gray-900 text-white text-center py-20">
          <Hero />
        </section>
      </div>
    </>
  );
}
