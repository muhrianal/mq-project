import React, { useEffect, useState } from "react";
import { fetchLessons } from "../api/api";
import { Link } from "react-router-dom";

export default function LessonList() {
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetchLessons()
      .then(setLessons)
      .catch(e => setErr(e.message || "Failed to load"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-4">Loading…</div>;
  if (err) return <div className="p-4 text-red-600">Error: {err}</div>;

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 via-white to-white">
      <div className="max-w-xl mx-auto p-4 space-y-4">
        <h2 className="text-lg font-semibold text-gray-800">Choose a lesson</h2>

        <ul className="space-y-3">
          {lessons.map((lesson, idx) => (
            <li key={lesson.id} className="bg-white border border-gray-100 rounded-2xl shadow-sm p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-gray-900 font-semibold">{lesson.title}</div>
                  <div className="mt-1 text-xs text-gray-500">
                    {lesson.problems?.length || 0} questions
                  </div>
                </div>
                <Link
                  to={`/lessons/${lesson.id}`}
                  className="inline-flex items-center px-4 py-2 rounded-xl text-white font-semibold bg-blue-600 hover:bg-blue-700 active:scale-[0.99] transition"
                >
                  Start
                </Link>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
