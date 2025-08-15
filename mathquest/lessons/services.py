# lessons/services.py
from datetime import datetime, timezone, timedelta
from users.models import User
from .models import Lesson, Problem, ProblemOption
from .models import UserProblemProgress  # <-- make sure this model exists (unique per user/problem)

XP_PER_CORRECT = 10  # XP awarded once per problem when it becomes correct


def evaluate_answers(user: User, lesson: Lesson, answers):
    """
    answers: list of dicts like:
      - {"problem_id": int, "option_id": int}
      - {"problem_id": int, "value": number}

    Returns: (correct_count, earned_xp, details)
      - correct_count: number correct in THIS submission
      - earned_xp: XP granted ONLY for problems that transitioned to correct (first time)
      - details: {problem_id: bool_is_correct}
    """
    correct_count = 0
    earned_xp = 0
    details = {}

    for a in answers:
        pid = a.get("problem_id")
        if pid is None:
            raise ValueError("InvalidAnswerFormat")

        try:
            problem = Problem.objects.get(pk=pid, lesson=lesson)
        except Problem.DoesNotExist:
            raise ValueError(f"InvalidProblem:{pid}")

        # Determine correctness for this submission
        if "option_id" in a:
            try:
                opt = ProblemOption.objects.get(pk=a["option_id"], problem=problem)
                is_correct = (problem.correct_option_id == opt.id)
            except ProblemOption.DoesNotExist:
                is_correct = False
        elif "value" in a:
            try:
                submitted = float(a["value"])
                is_correct = (
                    problem.correct_value is not None
                    and abs(problem.correct_value - submitted) < 1e-6
                )
            except Exception:
                is_correct = False
        else:
            raise ValueError("InvalidAnswerFormat")

        details[pid] = is_correct

        if is_correct:
            correct_count += 1
            # Award XP only if this problem becomes correct for the first time for this user
            progress, created = UserProblemProgress.objects.get_or_create(
                user=user, problem=problem, defaults={"solved_correctly": True}
            )
            if created or not progress.solved_correctly:
                # First ever correct (created) OR was previously incorrect and now correct
                earned_xp += XP_PER_CORRECT
                if not progress.solved_correctly:
                    progress.solved_correctly = True
                    progress.save()

    return correct_count, earned_xp, details


def compute_streak_and_update(user: User, earned_xp: int, commit: bool = False):
    """
    Computes streak transitions based on UTC day and adds earned_xp to user.total_xp.
    If commit=True, persists changes on user.
    Returns dict: {"current", "best", "new_total_xp", "prev_last_activity_date"}
    """
    today = datetime.now(timezone.utc).date()
    last = user.last_activity_date
    yesterday = today - timedelta(days=1)

    if last is None:
        new_streak = 1
    elif last == today:
        new_streak = user.current_streak
    elif last == yesterday:
        new_streak = user.current_streak + 1
    else:
        new_streak = 1

    new_total_xp = user.total_xp + earned_xp
    new_best = max(user.best_streak, new_streak)

    if commit:
        user.total_xp = new_total_xp
        user.current_streak = new_streak
        user.best_streak = new_best
        user.last_activity_date = today
        user.save()

    return {
        "current": new_streak,
        "best": new_best,
        "new_total_xp": new_total_xp,
        "prev_last_activity_date": last,
    }
