# lessons/management/commands/seed_data.py
from django.core.management.base import BaseCommand
from users.models import User
from lessons.models import Lesson, Problem, ProblemOption

class Command(BaseCommand):
    help = "Seed DB with demo user and 3 lessons"

    def handle(self, *args, **kwargs):
        user, _ = User.objects.get_or_create(pk=1, defaults={"username":"demo_user"})
        print("User 1:", user)

        # Lesson 1: Basic Arithmetic
        l1, _ = Lesson.objects.get_or_create(title="Basic Arithmetic")
        # Problem 101
        p1 = Problem.objects.create(lesson=l1, question_text="What is 2 + 3?")
        ProblemOption.objects.create(problem=p1, text="4")
        p1_correct_option = ProblemOption.objects.create(problem=p1, text="5")
        ProblemOption.objects.create(problem=p1, text="6")
        p1.correct_option = p1_correct_option
        p1.save()

        p2 = Problem.objects.create(lesson=l1, question_text="What is 7 - 2?")
        ProblemOption.objects.create(problem=p2, text="4")
        p2_correct_option = ProblemOption.objects.create(problem=p2, text="5")

        p2.correct_option = p2_correct_option
        p2.save()

        p3 = Problem.objects.create(lesson=l1, question_text="What is 10 + 0?")
        p3_correct_option = ProblemOption.objects.create(problem=p3, text="10")
        ProblemOption.objects.create(problem=p3, text="0")
        p3.correct_option = p3_correct_option
        p3.save()

        # Lesson 2: Multiplication Mastery
        l2, _ = Lesson.objects.get_or_create(title="Multiplication Mastery")
        p4 = Problem.objects.create(lesson=l2, question_text="3 x 4 = ?")
        p4_correct_option = ProblemOption.objects.create(problem=p4, text="12")
        ProblemOption.objects.create(problem=p4, text="7")
        p4.correct_option = p4_correct_option
        p4.save()

        p5 = Problem.objects.create(lesson=l2, question_text="6 x 6 = ?")
        p5_correct_option = ProblemOption.objects.create(problem=p5, text="36")
        ProblemOption.objects.create(problem=p5, text="42")
        p5.correct_option = p5_correct_option
        p5.save()

        p6 = Problem.objects.create(lesson=l2, question_text="5 x 0 = ?")
        p6_correct_option = ProblemOption.objects.create(problem=p6, text="0")
        ProblemOption.objects.create(problem=p6, text="5")
        p6.correct_option = p6_correct_option
        p6.save()

        # Lesson 3: Division Basics (an open numeric problem example)
        l3, _ = Lesson.objects.get_or_create(title="Division Basics")
        p7 = Problem.objects.create(lesson=l3, question_text="What is 10 / 2?", correct_value=5.0)
        p8 = Problem.objects.create(lesson=l3, question_text="What is 9 / 3?", correct_value=3.0)
        p9 = Problem.objects.create(lesson=l3, question_text="What is 8 / 2?", correct_value=4.0)

        print("Seeded lessons and problems.")
