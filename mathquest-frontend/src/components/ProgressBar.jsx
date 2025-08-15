export default function ProgressBar({ value=0 }) {
  const pct = Math.min(100, Math.max(0, Math.round(value * 100)));
  return (
    <div className="w-full bg-gray-100 rounded-full h-2">
      <div className="h-2 rounded-full transition-all duration-500" style={{ width: `${pct}%`, background: "linear-gradient(90deg,#60a5fa,#2563eb)" }} />
    </div>
  );
}
