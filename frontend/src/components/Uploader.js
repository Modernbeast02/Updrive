import { useRouter } from "next/router";
import React, { useState } from "react";
import { Spinner } from "flowbite-react";
import Loader from "./Loader";

export const Uploader = () => {
  const [file, setFile] = useState(null);
  const [isFilePresent, setIsFilePresent] = useState(false);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleFileChange = async (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setIsFilePresent(true);

      // Proceed to upload the file
      const formData = new FormData();
      formData.append("file", selectedFile); // Make sure key matches your backend

      try {
        setLoading(true);

        const response = await fetch("http://frontend.updrive.tech:5000/upload", {
          method: "POST",
          body: formData,
        });
        setLoading(false);
        if (response.ok) {
          alert("File uploaded successfully!");
          router.push(`/ChatBot?name=${selectedFile.name}`);
        } else {
          alert("Failed to upload the file.");
        }
      } catch (error) {
        console.error("Error:", error);
        alert("An error occurred while uploading the file.");
      }
    }
  };

  return (
    <>
      <section id="uploader" className="w-full flex justify-center pb-[250px]">
        {loading ? (
          <div className="-mb-60">
            <Loader />
          </div>
        ) : (
          <div className="flex items-center justify-center w-2/3">
            <label
              htmlFor="dropzone-file"
              className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-800 hover:bg-gray-600 duration-300"
            >
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <svg
                  className="w-8 h-8 mb-4 text-gray-500 dark:text-gray-400"
                  aria-hidden="true"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 20 16"
                >
                  <path
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"
                  />
                </svg>
                <p className="mb-2 text-sm text-gray-500 dark:text-gray-400">
                  <span className="font-semibold">Click to upload</span> or drag
                  and drop
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">PDF</p>
              </div>
              <input
                id="dropzone-file"
                type="file"
                className="hidden"
                onChange={handleFileChange}
              />
            </label>
          </div>
        )}
      </section>
    </>
  );
};
