import React, { useEffect, useState } from "react";
import { fetchLesson, submitLesson } from "../api/api";
import { useParams, Link } from "react-router-dom";

export default function LessonDetail() {
  const { id } = useParams();
  const [lesson, setLesson] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [err, setErr] = useState(null);

  useEffect(() => {
    setResult(null);
    setAnswers({});
    fetchLesson(id).then(setLesson).catch(e => setErr(e.message || "Failed to load"));
  }, [id]);

  const handleChange = (problemId, value) => {
    setAnswers(prev => ({ ...prev, [problemId]: value }));
  };

  const handleSubmit = async () => {
    if (!lesson) return;
    setSubmitting(true);
    setErr(null);
    try {
      const formatted = lesson.problems
        .map(p => {
          const val = answers[p.id];
          if (val === undefined || val === "" || val === null) return null;
          if (p.options && p.options.length > 0) {
            return { problem_id: p.id, option_id: parseInt(val, 10) };
          } else {
            return { problem_id: p.id, value: Number(val) };
          }
        })
        .filter(Boolean);

      const res = await submitLesson(id, formatted);
      setResult(res);
    } catch (e) {
      setErr(e.message || "Submit failed");
    } finally {
      setSubmitting(false);
    }
  };

  if (!lesson) {
    return (
      <div className="p-4">
        <Link to="/" className="text-blue-600 hover:underline">← Back</Link>
        <div className="mt-4">Loading…</div>
      </div>
    );
  }

  const progressPct = Math.round(((result?.lesson_progress ?? 0) * 100));

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 via-white to-white">
      <div className="max-w-xl mx-auto p-4 space-y-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="text-blue-600 hover:underline">← Back</Link>
          <h1 className="text-xl font-extrabold text-blue-800">{lesson.title}</h1>
          <div className="w-20 text-right text-xs text-gray-600">{progressPct ? `${progressPct}%` : ""}</div>
        </div>

        {lesson.problems.map((p, i) => (
          <div key={p.id} className="bg-white border border-gray-100 rounded-2xl shadow-sm p-4">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold grid place-items-center">{i+1}</div>
              <div className="flex-1">
                <div className="font-semibold text-gray-900">{p.question_text}</div>

                {p.options && p.options.length > 0 ? (
                  <select
                    className="mt-2 w-full border rounded-lg p-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    value={answers[p.id] ?? ""}
                    onChange={(e) => handleChange(p.id, e.target.value)}
                  >
                    <option value="">Select answer</option>
                    {p.options.map(o => (
                      <option key={o.id} value={o.id}>{o.text}</option>
                    ))}
                  </select>
                ) : (
                  <input
                    type="number"
                    placeholder="Type your answer"
                    className="mt-2 w-full border rounded-lg p-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    value={answers[p.id] ?? ""}
                    onChange={(e) => handleChange(p.id, e.target.value)}
                  />
                )}
              </div>
            </div>
          </div>
        ))}

        <div className="flex gap-3">
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="inline-flex items-center px-4 py-2 rounded-xl text-white font-semibold bg-blue-600 hover:bg-blue-700 active:scale-[0.99] transition disabled:opacity-60"
          >
            {submitting ? "Submitting..." : "Submit answers"}
          </button>
          <button
            className="px-4 py-2 rounded-xl font-semibold border border-gray-300 text-gray-700 hover:bg-gray-50"
            onClick={() => { setAnswers({}); setResult(null); }}
          >
            Reset
          </button>
        </div>

        {err && <div className="text-red-600">{err}</div>}

        {result && (
          <div className="bg-white border border-blue-100 rounded-2xl shadow-sm p-4">
            <div className="flex items-start gap-4">
              <div className="text-4xl">🎉</div>
              <div className="flex-1">
                <div className="text-lg font-bold text-gray-900">Great job!</div>
                <div className="text-sm text-gray-700 mt-1">
                  Correct: <b>{result.correct_count}</b>
                  {" · "}
                  Earned XP: <b>{result.earned_xp}</b>
                  {" · "}
                  Total XP: <b>{result.new_total_xp}</b>
                </div>
                <div className="text-sm text-gray-700 mt-1">
                  Streak: <b>{result.streak.current}</b> (best {result.streak.best})
                </div>
                <div className="mt-3">
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div
                      className="h-2 rounded-full transition-all"
                      style={{ width: `${progressPct}%`, background: "linear-gradient(90deg,#60a5fa,#2563eb)" }}
                    />
                  </div>
                  <div className="text-right text-xs text-gray-500 mt-1">
                    {progressPct}% complete
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
