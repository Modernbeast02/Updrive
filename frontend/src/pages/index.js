import Image from "next/image";
import localFont from "next/font/local";
import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import { Uploader } from "@/components/Uploader";

export default function Home() {
  return (
    <>
      <div className="h-full w-screen bg-gray-900 pb-10">
        <Navbar />
        <section className="bg-gray-900 text-white text-center py-20">
          <Hero />
        </section>
        <Uploader />
      </div>
    </>
  );
}
