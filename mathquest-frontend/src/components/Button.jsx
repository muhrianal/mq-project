export default function Button({ children, className="", ...props }) {
  return (
    <button
      className={`inline-flex items-center justify-center px-4 py-2 rounded-xl text-white font-semibold
                  bg-blue-600 hover:bg-blue-700 active:scale-[0.99] transition disabled:opacity-60 disabled:cursor-not-allowed ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
