import Link from "next/link";
import { TypeAnimation } from "react-type-animation";
const Hero = () => {
  return (
    <section className=" text-[#b7e4ea] text-center py-10">
      <h1 className="p-5 text-7xl mb-6 font-generalsans">Welcome To UPDRIVE</h1>
      <p className="text-6xl mb-6 font-generalsans text-color-gradient2">
        Smart PDF Companion
      </p>
      <TypeAnimation
        sequence={[
          "Innovative",
          1500,
          "Creative",
          1500,
          "Reliable",
          1500,
          "Efficient",
          1500,
          "Future-Ready",
          1500,
        ]}
        wrapper="span"
        cursor={true}
        repeat={10}
        style={{ fontSize: "60px" }}
      />

      <p className="text-lg mb-6 font-generalsans text-color-gradient2">
        Your one stop destination to upload pdfs
      </p>
      <div className="flex justify-center items-center pt-6">
        <button className=" text-white mb-80 py-2 px-6 rounded-lg getStartedButton hover:scale-[1.05] duration-300">
          <Link href="#uploader"> Get Started</Link>
        </button>
      </div>
    </section>
  );
};

export default Hero;
