import Link from "next/link";
import { useSession, signIn, signOut } from "next-auth/react";
const Navbar = () => {
  const { data: session } = useSession();
  if (session) {
    return (
      <>
        <nav className="flex justify-between items-center py-6 px-10 bg-gray-900 text-[#b7e4ea]">
          <div className="text-xl font-bold">Updrive</div>
          <div className="flex space-x-6">
            <Link href="#how-it-works">How it works</Link>
            <Link href="#why-us">Why Updrive</Link>
            <Link href="#features">Features</Link>
            <Link href="#blog">Blog</Link>
          </div>
          <div>
            <button
              onClick={() => signOut()()}
              className="px-4 py-2 mr-4 border border-gray-500 rounded"
            >
              {session.user.email}
            </button>
          </div>
        </nav>
      </>
    );
  } else {
    return (
      <>
        <nav className="flex justify-between items-center py-6 px-10 bg-gray-900 text-[#b7e4ea]">
          <div className="text-xl font-bold">Updrive</div>
          <div className="flex space-x-6">
            <Link href="#how-it-works">How it works</Link>
            <Link href="#why-us">Why Updrive</Link>
            <Link href="#features">Features</Link>
            <Link href="#blog">Blog</Link>
          </div>
          <div>
            <button
              onClick={() => signIn()}
              className="px-4 py-2 mr-4 border border-gray-500 rounded"
            >
              Sign In
            </button>
          </div>
        </nav>
      </>
    );
  }
};

export default Navbar;
