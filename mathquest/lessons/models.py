from django.db import models

class Lesson(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class Problem(models.Model):
    lesson = models.ForeignKey(Lesson, related_name="problems", on_delete=models.CASCADE)
    question_text = models.TextField()
    # For multiple choice problems, correct_option points to ProblemOption.
    # For open numeric problems, set correct_value instead.
    correct_option = models.ForeignKey("ProblemOption", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    correct_value = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Problem {self.id} - {self.lesson.title}"

class ProblemOption(models.Model):
    problem = models.ForeignKey(Problem, related_name="options", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"Option {self.id} for Problem {self.problem_id}"

class UserProblemProgress(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    problem = models.ForeignKey("lessons.Problem", on_delete=models.CASCADE)
    solved_correctly = models.BooleanField(default=False)
    solved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "problem")

