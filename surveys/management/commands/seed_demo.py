from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from surveys.models import Choice, Question, Survey


class Command(BaseCommand):
    help = 'Создаёт демонстрационный опрос'

    def handle(self, *args, **options):
        author, _ = get_user_model().objects.get_or_create(username='author')
        survey, created = Survey.objects.get_or_create(
            title='Овощи', author=author,
            defaults={'description': 'Небольшой опрос о ваших предпочтениях'}
        )
        if not created:
            self.stdout.write('Демонстрационный опрос уже существует')
            return

        data = [
            ('Ты любишь буратту с помидорами?', [
                'Да', 'Нет', 'У меня непереносимость лактозы'
            ], False),
            ('Ты любишь огурцы?', ['Да', 'Нет', 'Только в коктейлях'], True),
            ('Ты любишь помидоры?', ['Да', 'Нет', 'Только если гаспаччо'], True),
        ]
        for question_order, (text, choices, custom) in enumerate(data, start=1):
            question = Question.objects.create(
                survey=survey, text=text, order=question_order,
                allow_custom_answer=custom
            )
            Choice.objects.bulk_create([
                Choice(question=question, text=value, order=choice_order)
                for choice_order, value in enumerate(choices, start=1)
            ])
        self.stdout.write(self.style.SUCCESS('Демонстрационный опрос создан'))
