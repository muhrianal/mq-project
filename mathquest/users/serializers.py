from rest_framework import serializers
from .models import User

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "total_xp", "current_streak", "best_streak", "last_activity_date")
