export default function Badge({ children, color="blue" }) {
  const map = {
    blue: "text-blue-700 bg-blue-100",
    green: "text-green-700 bg-green-100",
    gray: "text-gray-700 bg-gray-100",
  };
  return <span className={`px-2 py-0.5 text-xs rounded-full font-medium ${map[color]}`}>{children}</span>;
}
