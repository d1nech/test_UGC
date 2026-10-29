from rest_framework import serializers
from .models import Choice, Question


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('id', 'text', 'order')


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'order', 'allow_custom_answer', 'choices')


class SubmitAnswerSerializer(serializers.Serializer):
    user = serializers.CharField(max_length=150)
    question_id = serializers.IntegerField()
    choice_id = serializers.IntegerField(required=False, allow_null=True)
    custom_answer = serializers.CharField(required=False, allow_blank=True,
                                          max_length=2000)

    def validate(self, data):
        if not data.get('choice_id') and not data.get('custom_answer', '').strip():
            raise serializers.ValidationError('Выберите вариант или введите свой ответ')
        return data
