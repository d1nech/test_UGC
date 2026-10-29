from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Attempt, Choice, Question, Survey
from .serializers import QuestionSerializer, SubmitAnswerSerializer
from .services import get_next_question, save_answer


@api_view(['GET'])
def next_question(request, survey_id):
    username = request.query_params.get('user', '').strip()
    if not username:
        return Response({'detail': 'Параметр user обязателен'}, status=400)

    survey = get_object_or_404(Survey, pk=survey_id, is_active=True)
    user, _ = get_user_model().objects.get_or_create(username=username)
    attempt, _ = Attempt.objects.get_or_create(survey=survey, user=user)
    question = get_next_question(attempt)
    if question is None:
        return Response({'completed': True, 'question': None})
    return Response({
        'completed': False,
        'progress': {
            'answered': attempt.answers.count(),
            'total': survey.questions.count(),
        },
        'question': QuestionSerializer(question).data,
    })


@api_view(['POST'])
def submit_answer(request, survey_id):
    serializer = SubmitAnswerSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    survey = get_object_or_404(Survey, pk=survey_id, is_active=True)
    user, _ = get_user_model().objects.get_or_create(username=data['user'])
    attempt, _ = Attempt.objects.get_or_create(survey=survey, user=user)
    try:
        answer, next_item = save_answer(
            attempt, data['question_id'], data.get('choice_id'),
            data.get('custom_answer', '')
        )
    except (ValueError, Question.DoesNotExist, Choice.DoesNotExist) as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({
        'answer_id': answer.id,
        'completed': next_item is None,
        'next_question_id': next_item.id if next_item else None,
    }, status=status.HTTP_201_CREATED)
