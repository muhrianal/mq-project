# submissions/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404

from users.models import User
from lessons.models import Lesson, Problem
from lessons.models import UserProblemProgress  # for progress calculation
from .models import SubmissionResult
from .serializers import SubmitSerializer
from lessons.services import evaluate_answers, compute_streak_and_update


class LessonSubmitView(APIView):
    """
    POST /api/lessons/{id}/submit
    Body: { "attempt_id": UUID, "answers": [ ... ] }
    - Idempotent via attempt_id
    - XP is granted only for problems that become correct for the first time
    """

    def post(self, request, id):
        serializer = SubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": "Validation", "message": serializer.errors}, status=400)

        data = serializer.validated_data
        attempt_id = data["attempt_id"]
        answers = data["answers"]
        if not answers:
            return Response({"error": "Validation", "message": "answers must be non-empty"}, status=400)

        lesson = get_object_or_404(Lesson, pk=id)
        user = get_object_or_404(User, pk=1)  # demo user per spec

        # If attempt already processed, return stored result (idempotent)
        prev = SubmissionResult.objects.filter(pk=attempt_id).first()
        if prev:
            resp = {
                "correct_count": prev.correct_count,
                "earned_xp": prev.earned_xp,
                "new_total_xp": user.total_xp,  # current total (no change on duplicate)
                "streak": {"current": user.current_streak, "best": user.best_streak},
                "lesson_progress": self._compute_progress(user, lesson),
                "duplicate": True,
            }
            return Response(resp, status=200)

        # Evaluate & apply within one transaction for safety
        with transaction.atomic():
            # Lock user row to avoid race in XP/streak
            user_locked = User.objects.select_for_update().get(pk=user.pk)

            # Re-check idempotency inside the transaction
            if SubmissionResult.objects.filter(pk=attempt_id).exists():
                prev = SubmissionResult.objects.get(pk=attempt_id)
                resp = {
                    "correct_count": prev.correct_count,
                    "earned_xp": prev.earned_xp,
                    "new_total_xp": user_locked.total_xp,
                    "streak": {"current": user_locked.current_streak, "best": user_locked.best_streak},
                    "lesson_progress": self._compute_progress(user_locked, lesson),
                    "duplicate": True,
                }
                return Response(resp, status=200)

            # Evaluate (this also upgrades UserProblemProgress where appropriate)
            try:
                correct_count, earned_xp, details = evaluate_answers(user_locked, lesson, answers)
            except ValueError as e:
                msg = str(e)
                if msg.startswith("InvalidProblem:"):
                    pid = msg.split(":")[1]
                    return Response({"error": "InvalidProblem", "message": f"Problem {pid} not found"}, status=422)
                return Response({"error": "Validation", "message": msg}, status=400)

            # Update streak & XP
            streak_info = compute_streak_and_update(user_locked, earned_xp, commit=True)

            # Persist attempt outcome for idempotency
            SubmissionResult.objects.create(
                attempt_id=attempt_id,
                user=user_locked,
                lesson=lesson,
                correct_count=correct_count,
                earned_xp=earned_xp,
                details=details,
            )

        resp = {
            "correct_count": correct_count,
            "earned_xp": earned_xp,  # only newly-correct problems grant XP
            "new_total_xp": streak_info["new_total_xp"],
            "streak": {"current": streak_info["current"], "best": streak_info["best"]},
            "lesson_progress": self._compute_progress(user_locked, lesson),
            "duplicate": False,
        }
        return Response(resp, status=200)

    def _compute_progress(self, user: User, lesson: Lesson) -> float:
        """
        Progress = (# problems solved_correctly for this lesson) / (total problems)
        Rounded to 3 decimals.
        """
        total = lesson.problems.count()
        if total == 0:
            return 0.0
        solved = UserProblemProgress.objects.filter(
            user=user, problem__lesson=lesson, solved_correctly=True
        ).count()
        return round(min(1.0, solved / total), 3)
