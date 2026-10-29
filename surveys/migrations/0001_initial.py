import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                             related_name='created_surveys',
                                             to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500)),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('allow_custom_answer', models.BooleanField(default=False)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                             related_name='questions', to='surveys.survey')),
            ],
            options={'ordering': ['order', 'id']},
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=300)),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                               related_name='choices', to='surveys.question')),
            ],
            options={'ordering': ['order', 'id']},
        ),
        migrations.CreateModel(
            name='Attempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                             related_name='attempts', to='surveys.survey')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='survey_attempts',
                                           to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('custom_answer', models.TextField(blank=True)),
                ('answered_at', models.DateTimeField(auto_now_add=True)),
                ('attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='answers', to='surveys.attempt')),
                ('choice', models.ForeignKey(blank=True, null=True,
                                             on_delete=django.db.models.deletion.SET_NULL,
                                             related_name='answers', to='surveys.choice')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                               related_name='answers', to='surveys.question')),
            ],
        ),
        migrations.CreateModel(
            name='SurveyStatistic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('completed_count', models.PositiveBigIntegerField(default=0)),
                ('total_duration_ms', models.PositiveBigIntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('survey', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                                                related_name='statistic', to='surveys.survey')),
            ],
        ),
        migrations.AddConstraint(
            model_name='question',
            constraint=models.UniqueConstraint(fields=('survey', 'order'),
                                               name='unique_question_order'),
        ),
        migrations.AddConstraint(
            model_name='choice',
            constraint=models.UniqueConstraint(fields=('question', 'order'),
                                               name='unique_choice_order'),
        ),
        migrations.AddIndex(
            model_name='attempt',
            index=models.Index(fields=['user', 'survey'], name='attempt_user_survey_idx'),
        ),
        migrations.AddConstraint(
            model_name='attempt',
            constraint=models.UniqueConstraint(fields=('survey', 'user'),
                                               name='one_attempt_per_user'),
        ),
        migrations.AddIndex(
            model_name='answer',
            index=models.Index(fields=['attempt', 'question'],
                               name='answer_attempt_question_idx'),
        ),
        migrations.AddConstraint(
            model_name='answer',
            constraint=models.UniqueConstraint(fields=('attempt', 'question'),
                                               name='one_answer_per_question'),
        ),
    ]
