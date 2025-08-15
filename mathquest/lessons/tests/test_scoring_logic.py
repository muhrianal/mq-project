from datetime import timedelta
import uuid

from django.test import TestCase
from django.utils import timezone

from users.models import User
from lessons.models import Lesson, Problem, ProblemOption
from submissions.models import SubmissionResult


class ScoringLogicTests(TestCase):
    """Covers streak transitions + idempotent scoring + XP upgrade (first-time per problem)."""

    def setUp(self):
        # Demo user id=1 per spec
        self.user = User.objects.create(pk=1, username="demo")

        # One lesson with 3 problems: 2 MCQ + 1 numeric
        self.lesson = Lesson.objects.create(title="Mixed Set")

        # P1: MCQ (correct option = o12)
        self.p1 = Problem.objects.create(lesson=self.lesson, question_text="2 + 2 = ?")
        o11 = ProblemOption.objects.create(problem=self.p1, text="3")
        o12 = ProblemOption.objects.create(problem=self.p1, text="4")  # correct
        o13 = ProblemOption.objects.create(problem=self.p1, text="5")
        self.p1.correct_option = o12
        self.p1.save()

        # P2: MCQ (correct option = o22)
        self.p2 = Problem.objects.create(lesson=self.lesson, question_text="3 + 4 = ?")
        o21 = ProblemOption.objects.create(problem=self.p2, text="6")
        o22 = ProblemOption.objects.create(problem=self.p2, text="7")  # correct
        self.p2.correct_option = o22
        self.p2.save()

        # P3: numeric
        self.p3 = Problem.objects.create(lesson=self.lesson, question_text="10 / 2 = ?", correct_value=5.0)

        # Precompute ids for convenience
        self.o12_id = self.p1.correct_option_id
        self.o22_id = self.p2.correct_option_id

    def _submit(self, answers, attempt_id=None):
        """Helper: POST /api/lessons/:id/submit with given answers."""
        if attempt_id is None:
            attempt_id = str(uuid.uuid4())
        body = {"attempt_id": attempt_id, "answers": answers}
        url = f"/api/lessons/{self.lesson.id}/submit"
        return self.client.post(url, data=body, content_type="application/json")

    def test_idempotent_scoring_same_attempt(self):
        """Same attempt_id twice => same response, no extra XP."""
        attempt = str(uuid.uuid4())
        answers = [
            {"problem_id": self.p1.id, "option_id": self.o12_id},  # correct
            {"problem_id": self.p2.id, "option_id": 999999},       # wrong option
            {"problem_id": self.p3.id, "value": 5},                # correct
        ]
        r1 = self._submit(answers, attempt_id=attempt)
        self.assertEqual(r1.status_code, 200)
        data1 = r1.json()
        self.assertEqual(data1["correct_count"], 2)
        self.assertEqual(data1["earned_xp"], 20)
        total_after_first = data1["new_total_xp"]

        # resend same attempt
        r2 = self._submit(answers, attempt_id=attempt)
        self.assertEqual(r2.status_code, 200)
        data2 = r2.json()
        self.assertTrue(data2.get("duplicate", False))
        # total XP stays the same
        self.assertEqual(data2["new_total_xp"], total_after_first)
        self.assertEqual(User.objects.get(pk=1).total_xp, total_after_first)

    def test_xp_upgrade_when_fixing_wrong_answer(self):
        """
        Attempt 1: 2/3 correct => +20 XP
        Attempt 2 (new attempt id): now 3/3 correct => +10 XP more (total 30), not 50
        """
        # Attempt 1 (P1 correct, P2 wrong, P3 correct)
        a1 = [
            {"problem_id": self.p1.id, "option_id": self.o12_id},
            {"problem_id": self.p2.id, "option_id": 123456},  # wrong
            {"problem_id": self.p3.id, "value": 5},
        ]
        r1 = self._submit(a1)
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.json()["earned_xp"], 20)
        self.assertEqual(User.objects.get(pk=1).total_xp, 20)

        # Attempt 2 (fix P2 to correct) => +10 XP only
        a2 = [
            {"problem_id": self.p1.id, "option_id": self.o12_id},  # already correct before -> 0 XP
            {"problem_id": self.p2.id, "option_id": self.o22_id},  # now correct -> +10
            {"problem_id": self.p3.id, "value": 5},                # already correct before -> 0 XP
        ]
        r2 = self._submit(a2)
        self.assertEqual(r2.status_code, 200)
        data2 = r2.json()
        self.assertEqual(data2["earned_xp"], 10)
        self.assertEqual(User.objects.get(pk=1).total_xp, 30)

    def test_streak_transitions_same_day_then_next_day_then_skip(self):
        """
        - First submit today: streak becomes 1
        - Second submit same UTC day: streak unchanged
        - Third submit next day (no gap): streak +1
        - Fourth submit after skipping a day: streak resets to 1
        """
        # First submit (today)
        r1 = self._submit([
            {"problem_id": self.p1.id, "option_id": self.o12_id},
        ])
        self.assertEqual(r1.status_code, 200)
        u = User.objects.get(pk=1)
        self.assertEqual(u.current_streak, 1)

        # Second submit same day => unchanged
        r2 = self._submit([
            {"problem_id": self.p2.id, "option_id": self.o22_id},
        ])
        u.refresh_from_db()
        self.assertEqual(u.current_streak, 1)

        # Simulate tomorrow
        yesterday = timezone.now().date() - timedelta(days=1)
        User.objects.filter(pk=1).update(last_activity_date=yesterday, current_streak=1)

        # Third submit (next day) => +1
        r3 = self._submit([
            {"problem_id": self.p3.id, "value": 5},
        ])
        u.refresh_from_db()
        self.assertEqual(u.current_streak, 2)

        # Simulate skipping one day (last activity 2 days ago)
        two_days_ago = timezone.now().date() - timedelta(days=2)
        User.objects.filter(pk=1).update(last_activity_date=two_days_ago, current_streak=5)

        # Fourth submit after skip => reset to 1
        r4 = self._submit([
            {"problem_id": self.p1.id, "option_id": self.o12_id},
        ])
        u.refresh_from_db()
        self.assertEqual(u.current_streak, 1)
