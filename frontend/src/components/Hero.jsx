const Hero = () => {
  return (
    <section className=" text-[#b7e4ea] text-center py-20">
      <h1 className="p-5 text-7xl mb-6 font-generalsans">Welcome To UPDRIVE</h1>
      <p className="text-6xl mb-6 font-generalsans text-color-gradient2">
        Smart PDF Companion
      </p>
      <p className="text-lg mb-6 font-generalsans text-color-gradient2">
        Your one stop destination to upload pdfs
      </p>
      <div className="flex justify-center items-center pt-6">
        <button className=" text-white py-2 px-6 rounded-lg getStartedButton hover:scale-[1.05] duration-300">
          Get Started
        </button>
      </div>
    </section>
  );
};

export default Hero;
