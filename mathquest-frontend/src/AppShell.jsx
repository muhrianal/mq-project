export default function AppShell({ children }) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 via-white to-white">
      <div className="max-w-xl mx-auto px-4 pb-16">
        {children}
      </div>
    </div>
  );
}
