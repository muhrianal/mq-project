import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const { pathname } = useLocation();
  const isActive = (p) => pathname === p ? "text-white bg-blue-600" : "text-blue-600 bg-blue-100 hover:bg-blue-200";

  return (
    <header className="sticky top-0 z-20 backdrop-blur bg-white/70 border-b">
      <div className="max-w-xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="font-extrabold text-xl tracking-tight text-blue-700">MathQuest</Link>
        <nav className="flex gap-2">
          <Link to="/" className={`px-3 py-1.5 rounded-full text-sm font-medium transition ${isActive("/")}`}>Lessons</Link>
          <Link to="/profile" className={`px-3 py-1.5 rounded-full text-sm font-medium transition ${isActive("/profile")}`}>Profile</Link>
        </nav>
      </div>
    </header>
  );
}
