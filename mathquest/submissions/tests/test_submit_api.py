import uuid
from django.test import TestCase

from users.models import User
from lessons.models import Lesson, Problem, ProblemOption


class SubmitEndpointTests(TestCase):
    """Covers /api/lessons/:id/submit contract, idempotency, invalid problem 422, and mixed MCQ/numeric."""

    def setUp(self):
        self.user = User.objects.create(pk=1, username="demo")
        self.lesson = Lesson.objects.create(title="API Contract Lesson")

        # P1 MCQ (correct o1b)
        p1 = Problem.objects.create(lesson=self.lesson, question_text="5 + 5 = ?")
        o1a = ProblemOption.objects.create(problem=p1, text="9")
        o1b = ProblemOption.objects.create(problem=p1, text="10")  # correct
        p1.correct_option = o1b
        p1.save()

        # P2 numeric
        Problem.objects.create(lesson=self.lesson, question_text="6 / 2 = ?", correct_value=3.0)

        self.p1 = p1
        self.o1b_id = p1.correct_option_id
        self.p2 = Problem.objects.filter(lesson=self.lesson).exclude(pk=p1.pk).first()

    def test_submit_returns_expected_shape_and_status(self):
        attempt = str(uuid.uuid4())
        url = f"/api/lessons/{self.lesson.id}/submit"
        body = {
            "attempt_id": attempt,
            "answers": [
                {"problem_id": self.p1.id, "option_id": self.o1b_id},  # correct
                {"problem_id": self.p2.id, "value": 3},                # correct
            ]
        }
        r = self.client.post(url, data=body, content_type="application/json")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        # contract keys
        for key in ["correct_count", "earned_xp", "new_total_xp", "streak", "lesson_progress", "duplicate"]:
            self.assertIn(key, data)
        self.assertEqual(data["correct_count"], 2)
        self.assertGreaterEqual(data["earned_xp"], 20)  # first-time solves => at least 20
        self.assertIsInstance(data["streak"], dict)

    def test_idempotent_same_attempt_id(self):
        attempt = str(uuid.uuid4())
        url = f"/api/lessons/{self.lesson.id}/submit"
        body = {
            "attempt_id": attempt,
            "answers": [
                {"problem_id": self.p1.id, "option_id": self.o1b_id},
            ]
        }
        r1 = self.client.post(url, data=body, content_type="application/json")
        self.assertEqual(r1.status_code, 200)
        data1 = r1.json()
        total1 = data1["new_total_xp"]

        r2 = self.client.post(url, data=body, content_type="application/json")
        self.assertEqual(r2.status_code, 200)
        data2 = r2.json()
        self.assertTrue(data2.get("duplicate", False))
        self.assertEqual(data2["new_total_xp"], User.objects.get(pk=1).total_xp)
        self.assertEqual(User.objects.get(pk=1).total_xp, total1)

    def test_invalid_problem_id_returns_422(self):
        attempt = str(uuid.uuid4())
        url = f"/api/lessons/{self.lesson.id}/submit"
        body = {
            "attempt_id": attempt,
            "answers": [
                {"problem_id": 999999, "option_id": 1},  # invalid problem
            ]
        }
        r = self.client.post(url, data=body, content_type="application/json")
        self.assertEqual(r.status_code, 422)
        data = r.json()
        self.assertEqual(data.get("error"), "InvalidProblem")

    def test_upgrade_only_adds_missing_xp(self):
        """
        First submit: only P1 correct => +10
        Second submit (new attempt id): P1 still correct, P2 now correct => +10 (total 20), not 30.
        """
        url = f"/api/lessons/{self.lesson.id}/submit"

        # Submit 1
        a1 = {
            "attempt_id": str(uuid.uuid4()),
            "answers": [
                {"problem_id": self.p1.id, "option_id": self.o1b_id},  # correct
                {"problem_id": self.p2.id, "value": 999},              # wrong
            ]
        }
        r1 = self.client.post(url, data=a1, content_type="application/json")
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.json()["earned_xp"], 10)
        total_after_1 = r1.json()["new_total_xp"]

        # Submit 2 (fix P2)
        a2 = {
            "attempt_id": str(uuid.uuid4()),
            "answers": [
                {"problem_id": self.p1.id, "option_id": self.o1b_id},  # already correct -> 0
                {"problem_id": self.p2.id, "value": 3},                # now correct -> +10
            ]
        }
        r2 = self.client.post(url, data=a2, content_type="application/json")
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.json()["earned_xp"], 10)
        self.assertEqual(r2.json()["new_total_xp"], total_after_1 + 10)
