from django.db import models

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    total_xp = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    best_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)  # stored as UTC date

    def __str__(self):
        return f"{self.username} ({self.id})"