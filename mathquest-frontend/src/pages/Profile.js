import React, { useEffect, useState } from "react";
import { fetchProfile } from "../api/api";
import Card from "../components/Card";

export default function Profile() {
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    fetchProfile().then(setProfile);
  }, []);

  if (!profile) return <div className="p-4">Loading...</div>;

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-extrabold text-blue-800">Your progress</h1>
      <Card className="p-4">
        <dl className="grid grid-cols-2 gap-4">
          <div>
            <dt className="text-xs text-gray-500">Username</dt>
            <dd className="text-lg font-semibold">{profile.username}</dd>
          </div>
          <div>
            <dt className="text-xs text-gray-500">Total XP</dt>
            <dd className="text-lg font-semibold text-blue-700">{profile.total_xp}</dd>
          </div>
          <div>
            <dt className="text-xs text-gray-500">Current Streak</dt>
            <dd className="text-lg font-semibold">{profile.current_streak}</dd>
          </div>
          <div>
            <dt className="text-xs text-gray-500">Best Streak</dt>
            <dd className="text-lg font-semibold">{profile.best_streak}</dd>
          </div>
          <div className="col-span-2">
            <dt className="text-xs text-gray-500">Last Activity</dt>
            <dd className="text-sm">{profile.last_activity_date || "—"}</dd>
          </div>
        </dl>
      </Card>
    </div>
  );
}
