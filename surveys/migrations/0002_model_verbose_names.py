from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [('surveys', '0001_initial')]

    operations = [
        migrations.AlterModelOptions(
            name='survey',
            options={'ordering': ['-created_at'], 'verbose_name': 'опрос',
                     'verbose_name_plural': 'Опросы'},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['order', 'id'], 'verbose_name': 'вопрос',
                     'verbose_name_plural': 'Вопросы'},
        ),
        migrations.AlterModelOptions(
            name='choice',
            options={'ordering': ['order', 'id'], 'verbose_name': 'вариант ответа',
                     'verbose_name_plural': 'Варианты ответов'},
        ),
        migrations.AlterModelOptions(
            name='attempt',
            options={'verbose_name': 'прохождение',
                     'verbose_name_plural': 'Прохождения'},
        ),
        migrations.AlterModelOptions(
            name='answer',
            options={'verbose_name': 'ответ', 'verbose_name_plural': 'Ответы'},
        ),
        migrations.AlterModelOptions(
            name='surveystatistic',
            options={'verbose_name': 'статистика опроса',
                     'verbose_name_plural': 'Статистика опросов'},
        ),
    ]
