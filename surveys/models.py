from django.conf import settings
from django.db import models


class Survey(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='created_surveys')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'опрос'
        verbose_name_plural = 'Опросы'

    def __str__(self):
        return self.title


class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE,
                               related_name='questions')
    text = models.CharField(max_length=500)
    order = models.PositiveSmallIntegerField(default=0)
    allow_custom_answer = models.BooleanField(default=False)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'вопрос'
        verbose_name_plural = 'Вопросы'
        constraints = [
            models.UniqueConstraint(fields=['survey', 'order'],
                                    name='unique_question_order')
        ]

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE,
                                 related_name='choices')
    text = models.CharField(max_length=300)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'вариант ответа'
        verbose_name_plural = 'Варианты ответов'
        constraints = [
            models.UniqueConstraint(fields=['question', 'order'],
                                    name='unique_choice_order')
        ]

    def __str__(self):
        return self.text


class Attempt(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE,
                               related_name='attempts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='survey_attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'прохождение'
        verbose_name_plural = 'Прохождения'
        constraints = [
            models.UniqueConstraint(fields=['survey', 'user'],
                                    name='one_attempt_per_user')
        ]
        indexes = [models.Index(fields=['user', 'survey'], name='attempt_user_survey_idx')]

    def __str__(self):
        return f'{self.user} — {self.survey}'


class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE,
                                related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE,
                                 related_name='answers')
    choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True,
                               blank=True, related_name='answers')
    custom_answer = models.TextField(blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'ответ'
        verbose_name_plural = 'Ответы'
        constraints = [
            models.UniqueConstraint(fields=['attempt', 'question'],
                                    name='one_answer_per_question')
        ]
        indexes = [models.Index(fields=['attempt', 'question'], name='answer_attempt_question_idx')]


class SurveyStatistic(models.Model):
    survey = models.OneToOneField(Survey, on_delete=models.CASCADE,
                                  related_name='statistic')
    completed_count = models.PositiveBigIntegerField(default=0)
    total_duration_ms = models.PositiveBigIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'статистика опроса'
        verbose_name_plural = 'Статистика опросов'

    @property
    def average_duration_seconds(self):
        if not self.completed_count:
            return 0
        return round(self.total_duration_ms / self.completed_count / 1000, 1)
