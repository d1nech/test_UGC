from django.contrib.auth import get_user_model
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from .models import Attempt, Choice, Survey, SurveyStatistic
from .services import get_next_question, save_answer


def survey_list(request):
    surveys = Survey.objects.filter(is_active=True).select_related('author')
    return render(request, 'surveys/list.html', {'surveys': surveys})


def survey_start(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id, is_active=True)
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        if username:
            user, _ = get_user_model().objects.get_or_create(username=username)
            attempt, _ = Attempt.objects.get_or_create(survey=survey, user=user)
            request.session['survey_user_id'] = user.id
            return redirect('survey-question', survey_id=survey.id)
    return render(request, 'surveys/start.html', {'survey': survey})


def survey_question(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id, is_active=True)
    user_id = request.session.get('survey_user_id')
    if not user_id:
        return redirect('survey-start', survey_id=survey.id)
    attempt = get_object_or_404(Attempt, survey=survey, user_id=user_id)
    question = get_next_question(attempt)
    if question is None:
        return redirect('survey-complete', survey_id=survey.id)

    error = ''
    if request.method == 'POST':
        try:
            save_answer(
                attempt, question.id, request.POST.get('choice') or None,
                request.POST.get('custom_answer', '')
            )
            return redirect('survey-question', survey_id=survey.id)
        except (ValueError, Choice.DoesNotExist) as exc:
            error = str(exc)

    answered = attempt.answers.count()
    total = survey.questions.count()
    progress = round(answered / total * 100) if total else 100
    return render(request, 'surveys/question.html', {
        'survey': survey, 'question': question, 'answered': answered,
        'total': total, 'progress': progress, 'error': error,
    })


def survey_complete(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    return render(request, 'surveys/complete.html', {'survey': survey})


def survey_stats(request, survey_id):
    survey = get_object_or_404(Survey.objects.select_related('author'), pk=survey_id)
    statistic, _ = SurveyStatistic.objects.get_or_create(survey=survey)
    questions = survey.questions.prefetch_related('choices').all()
    rows = []
    for question in questions:
        choices = question.choices.annotate(answer_count=Count('answers'))
        custom_count = question.answers.exclude(custom_answer='').count()
        rows.append({
            'question': question, 'choices': choices,
            'custom_count': custom_count,
        })
    return render(request, 'surveys/stats.html', {
        'survey': survey, 'statistic': statistic, 'rows': rows,
    })
