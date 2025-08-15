from rest_framework import serializers

class AnswerItemSerializer(serializers.Serializer):
    problem_id = serializers.IntegerField()
    option_id = serializers.IntegerField(required=False)
    value = serializers.FloatField(required=False)

class SubmitSerializer(serializers.Serializer):
    attempt_id = serializers.UUIDField()
    answers = AnswerItemSerializer(many=True)
