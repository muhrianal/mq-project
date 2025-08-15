import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import LessonList from "./pages/LessonList";
import LessonDetail from "./pages/LessonDetail";
import Profile from "./pages/Profile";
import Navbar from "./components/Navbar";
import AppShell from "./AppShell";

export default function App() {
  return (
    <Router>
      <Navbar/>
      <AppShell>
        <Routes>
          <Route path="/" element={<LessonList />} />
          <Route path="/lessons/:id" element={<LessonDetail />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </AppShell>
    </Router>
  );
}
