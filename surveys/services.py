from django.db import transaction
from django.db.models import F
from django.utils import timezone
from .models import Answer, Attempt, Choice, Question, SurveyStatistic


def get_next_question(attempt):
    answered = attempt.answers.values_list('question_id', flat=True)
    return attempt.survey.questions.prefetch_related('choices').exclude(
        id__in=answered
    ).first()


@transaction.atomic
def save_answer(attempt, question_id, choice_id=None, custom_answer=''):
    attempt = Attempt.objects.select_for_update().get(pk=attempt.pk)
    question = Question.objects.get(pk=question_id, survey=attempt.survey)
    expected_question = get_next_question(attempt)
    if expected_question is None or expected_question.id != question.id:
        raise ValueError('Сейчас нужно ответить на другой вопрос')
    if attempt.answers.filter(question=question).exists():
        raise ValueError('На этот вопрос уже дан ответ')

    choice = None
    if choice_id:
        choice = Choice.objects.get(pk=choice_id, question=question)
    custom_answer = custom_answer.strip()
    if custom_answer and not question.allow_custom_answer:
        raise ValueError('Свой ответ для этого вопроса запрещён')
    if not choice and not custom_answer:
        raise ValueError('Ответ не указан')

    answer = Answer.objects.create(
        attempt=attempt, question=question, choice=choice,
        custom_answer=custom_answer
    )
    next_question = get_next_question(attempt)
    if next_question is None:
        finished = timezone.now()
        attempt.completed_at = finished
        attempt.save(update_fields=['completed_at'])
        duration_ms = int((finished - attempt.started_at).total_seconds() * 1000)
        statistic, created = SurveyStatistic.objects.get_or_create(
            survey=attempt.survey
        )
        SurveyStatistic.objects.filter(pk=statistic.pk).update(
            completed_count=F('completed_count') + 1,
            total_duration_ms=F('total_duration_ms') + duration_ms
        )
    return answer, next_question
