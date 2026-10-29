from django.contrib import admin, messages
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Max
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import path, reverse
from .models import Answer, Attempt, Choice, Question, Survey, SurveyStatistic


admin.site.site_header = 'Опросы UGC'
admin.site.site_title = 'Панель управления'
admin.site.index_title = 'Управление данными'
admin.site.unregister(Group)


def swap_order(first, second):
    first_order = first.order
    second_order = second.order
    model = type(first)
    parent_filter = {'survey': first.survey} if model is Question else {
        'question': first.question
    }
    temporary = model.objects.filter(**parent_filter).aggregate(
        value=Max('order')
    )['value'] + 100
    first.order = temporary
    first.save(update_fields=['order'])
    second.order = first_order
    second.save(update_fields=['order'])
    first.order = second_order
    first.save(update_fields=['order'])


def move_item(item, direction, queryset):
    if direction == 'up':
        sibling = queryset.filter(order__lt=item.order).order_by('-order').first()
    else:
        sibling = queryset.filter(order__gt=item.order).order_by('order').first()
    if sibling:
        swap_order(item, sibling)


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    change_form_template = 'admin/surveys/survey/change_form.html'
    list_display = ('title', 'author', 'created_at', 'is_active', 'question_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'author__username')
    list_select_related = ('author',)

    @admin.display(description='Вопросов')
    def question_count(self, obj):
        return obj.questions.count()

    def get_urls(self):
        custom_urls = [
            path(
                '<path:object_id>/stats/',
                self.admin_site.admin_view(self.stats_view),
                name='surveys_survey_stats',
            ),
            path(
                '<path:object_id>/editor/',
                self.admin_site.admin_view(self.editor_view),
                name='surveys_survey_editor',
            ),
        ]
        return custom_urls + super().get_urls()

    def response_add(self, request, obj, post_url_continue=None):
        return HttpResponseRedirect(reverse(
            'admin:surveys_survey_editor', args=[obj.pk]
        ))

    def editor_view(self, request, object_id):
        survey = get_object_or_404(Survey, pk=object_id)
        if not self.has_change_permission(request, survey):
            raise PermissionDenied

        if request.method == 'POST':
            with transaction.atomic():
                self.process_editor_action(request, survey)
            return HttpResponseRedirect(reverse(
                'admin:surveys_survey_editor', args=[survey.pk]
            ))

        survey = Survey.objects.prefetch_related('questions__choices').get(pk=survey.pk)
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': f'Редактор: {survey.title}',
            'survey': survey,
            'has_view_permission': self.has_view_permission(request, survey),
            'has_change_permission': True,
        }
        return render(request, 'admin/surveys/survey/editor.html', context)

    def stats_view(self, request, object_id):
        survey = get_object_or_404(
            Survey.objects.select_related('author'), pk=object_id
        )
        if not self.has_view_permission(request, survey):
            raise PermissionDenied

        statistic, _ = SurveyStatistic.objects.get_or_create(survey=survey)
        started_count = survey.attempts.count()
        completion_rate = round(
            statistic.completed_count / started_count * 100
        ) if started_count else 0
        rows = []
        for question in survey.questions.prefetch_related('choices'):
            choices = question.choices.annotate(answer_count=Count('answers'))
            custom_answers = question.answers.exclude(
                custom_answer=''
            ).values_list('custom_answer', flat=True)[:20]
            rows.append({
                'question': question,
                'choices': choices,
                'custom_answers': custom_answers,
            })

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': f'Статистика: {survey.title}',
            'survey': survey,
            'statistic': statistic,
            'started_count': started_count,
            'completion_rate': completion_rate,
            'rows': rows,
            'has_view_permission': True,
        }
        return render(request, 'admin/surveys/survey/stats.html', context)

    def process_editor_action(self, request, survey):
        action = request.POST.get('action')
        if action == 'update_survey':
            title = request.POST.get('title', '').strip()
            if title:
                survey.title = title
                survey.description = request.POST.get('description', '').strip()
                survey.is_active = bool(request.POST.get('is_active'))
                survey.save(update_fields=['title', 'description', 'is_active'])
                self.message_user(request, 'Опрос сохранён', messages.SUCCESS)

        elif action == 'add_question':
            text = request.POST.get('text', '').strip()
            if text:
                last_order = survey.questions.aggregate(value=Max('order'))['value'] or 0
                Question.objects.create(
                    survey=survey, text=text, order=last_order + 1,
                    allow_custom_answer=bool(request.POST.get('allow_custom_answer')),
                )
                self.message_user(request, 'Вопрос добавлен', messages.SUCCESS)

        elif action in {'update_question', 'delete_question', 'move_question'}:
            question = get_object_or_404(survey.questions, pk=request.POST.get('question_id'))
            if action == 'update_question':
                text = request.POST.get('text', '').strip()
                if text:
                    question.text = text
                    question.allow_custom_answer = bool(
                        request.POST.get('allow_custom_answer')
                    )
                    question.save(update_fields=['text', 'allow_custom_answer'])
                    self.message_user(request, 'Вопрос сохранён', messages.SUCCESS)
            elif action == 'delete_question':
                question.delete()
                self.message_user(request, 'Вопрос удалён', messages.SUCCESS)
            else:
                move_item(question, request.POST.get('direction'), survey.questions)

        elif action == 'add_choice':
            question = get_object_or_404(survey.questions, pk=request.POST.get('question_id'))
            text = request.POST.get('text', '').strip()
            if text:
                last_order = question.choices.aggregate(value=Max('order'))['value'] or 0
                Choice.objects.create(question=question, text=text, order=last_order + 1)
                self.message_user(request, 'Вариант добавлен', messages.SUCCESS)

        elif action in {'update_choice', 'delete_choice', 'move_choice'}:
            choice = get_object_or_404(
                Choice.objects.filter(question__survey=survey),
                pk=request.POST.get('choice_id'),
            )
            if action == 'update_choice':
                text = request.POST.get('text', '').strip()
                if text:
                    choice.text = text
                    choice.save(update_fields=['text'])
                    self.message_user(request, 'Вариант сохранён', messages.SUCCESS)
            elif action == 'delete_choice':
                choice.delete()
                self.message_user(request, 'Вариант удалён', messages.SUCCESS)
            else:
                move_item(choice, request.POST.get('direction'), choice.question.choices)


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('survey', 'user', 'started_at', 'completed_at')
    list_filter = ('survey', 'completed_at')
    search_fields = ('user__username', 'survey__title')
    readonly_fields = ('survey', 'user', 'started_at', 'completed_at')

    def has_add_permission(self, request):
        return False


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'attempt', 'choice', 'answered_at')
    list_filter = ('question__survey',)
    readonly_fields = ('attempt', 'question', 'choice', 'custom_answer', 'answered_at')

    def has_add_permission(self, request):
        return False


@admin.register(SurveyStatistic)
class SurveyStatisticAdmin(admin.ModelAdmin):
    list_display = ('survey', 'completed_count', 'average_duration_seconds', 'updated_at')
    readonly_fields = ('survey', 'completed_count', 'total_duration_ms', 'updated_at')

    def has_add_permission(self, request):
        return False
