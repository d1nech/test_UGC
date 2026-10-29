from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Удаляет все данные из базы, сохраняя таблицы и миграции'

    def add_arguments(self, parser):
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Удалить данные без подтверждения',
        )

    def handle(self, *args, **options):
        if not options['yes']:
            answer = input('Будут удалены все данные. Введите DELETE: ')
            if answer != 'DELETE':
                raise CommandError('Удаление отменено')

        call_command('flush', interactive=False, verbosity=0)
        self.stdout.write(self.style.SUCCESS('Все данные удалены'))
