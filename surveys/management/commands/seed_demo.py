from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from surveys.models import Choice, Question, Survey


class Command(BaseCommand):
    help = 'Создаёт демонстрационный опрос'

    def handle(self, *args, **options):
        author, _ = get_user_model().objects.get_or_create(username='author')
        survey, _ = Survey.objects.get_or_create(
            title='Овощи', author=author,
            defaults={'description': 'Небольшой опрос о ваших предпочтениях'}
        )

        data = [
            ('Ты любишь буратту с помидорами?', [
                'Да', 'Нет', 'У меня непереносимость лактозы'
            ], False),
            ('Ты любишь огурцы?', ['Да', 'Нет', 'Только в коктейлях'], True),
            ('Ты любишь помидоры?', ['Да', 'Нет', 'Только если гаспаччо'], True),
            ('Ты любишь салат из огурцов?', [
                'Да', 'Нет', 'Только с уксусом'
            ], False),
            ('Ты любишь сладкий перец?', ['Да', 'Нет', 'Только запечённый'], False),
            ('Ты ешь брокколи?', ['Часто', 'Иногда', 'Никогда'], True),
            ('Как ты относишься к кабачкам?', [
                'Люблю', 'Не люблю', 'Ем только оладьи'
            ], False),
            ('Ты любишь баклажаны?', ['Да', 'Нет', 'Только на гриле'], False),
            ('Ты пьёшь морковный сок?', ['Да', 'Нет', 'Иногда'], True),
            ('Ты любишь тыквенный суп?', ['Да', 'Нет', 'Не пробовал'], False),
            ('Ты ешь кукурузу?', ['Да', 'Нет', 'Только в салате'], False),
            ('Ты любишь салат со свёклой?', ['Да', 'Нет', 'Иногда'], True),
            ('Ты ешь цветную капусту?', ['Да', 'Нет', 'Только запечённую'], False),
            ('Ты любишь редис?', ['Да', 'Нет', 'Только в салате'], False),
            ('Ты любишь овощное рагу?', ['Да', 'Нет', 'Зависит от рецепта'], True),
        ]
        for question_order, (text, choices, custom) in enumerate(data, start=1):
            question, _ = Question.objects.update_or_create(
                survey=survey, order=question_order,
                defaults={
                    'text': text,
                    'allow_custom_answer': custom,
                },
            )
            for choice_order, value in enumerate(choices, start=1):
                Choice.objects.update_or_create(
                    question=question, order=choice_order,
                    defaults={'text': value},
                )
        self.stdout.write(self.style.SUCCESS(
            'Демонстрационный опрос с 15 вопросами готов'
        ))
