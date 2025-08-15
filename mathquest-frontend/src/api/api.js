import { v4 as uuidv4 } from 'uuid';

const API_BASE = "http://127.0.0.1:8000/api";

export async function fetchLessons() {
  const res = await fetch(`${API_BASE}/lessons/`);
  return res.json();
}

export async function fetchLesson(id) {
  const res = await fetch(`${API_BASE}/lessons/${id}/`);
  return res.json();
}

export async function submitLesson(id, answers, attemptId = null) {
  if (!attemptId) attemptId = uuidv4();
  const res = await fetch(`${API_BASE}/lessons/${id}/submit`, {
    method: 'POST',
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ attempt_id: attemptId, answers })
  });
  return res.json();
}

export async function fetchProfile() {
  const res = await fetch(`${API_BASE}/profile`);
  return res.json();
}
