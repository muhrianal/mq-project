from django.db import models
from users.models import User
from lessons.models import Lesson

class SubmissionResult(models.Model):
    # Store the outcome for an attempt id (idempotency)
    attempt_id = models.UUIDField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    correct_count = models.IntegerField()
    earned_xp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    # store serialized details as JSON for returning same payload if re-submitted
    details = models.JSONField(default=dict)
