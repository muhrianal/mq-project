from rest_framework import serializers
from .models import Lesson, Problem, ProblemOption

class ProblemOptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model = ProblemOption
        fields = ("id", "text")

class ProblemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    options = ProblemOptionSerializer(many=True, read_only=True)
    class Meta:
        model = Problem
        fields = ("id", "question_text", "options")  # no correct_option/value
        # Note: We intentionally do not expose correct_option or correct_value

class LessonSerializer(serializers.ModelSerializer):
    problems = ProblemSerializer(many=True, read_only=True)
    class Meta:
        model = Lesson
        fields = ("id", "title", "problems")
