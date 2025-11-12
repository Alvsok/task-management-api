from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task, Comment, TaskStatus


class Command(BaseCommand):
    help = 'Создание тестовых данных для демонстрации API'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Создание тестовых данных...'))
        self.stdout.write('')

        # Создаем пользователей
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Админ',
                'last_name': 'Админов',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created or True:  # Всегда обновляем пароль
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(f'  {"✓ Создан" if created else "✓ Обновлен"} пользователь: admin')

        user1, created = User.objects.get_or_create(
            username='user1',
            defaults={
                'email': 'user1@example.com',
                'first_name': 'Иван',
                'last_name': 'Иванов'
            }
        )
        if created or True:
            user1.set_password('user123')
            user1.save()
            self.stdout.write(f'  {"✓ Создан" if created else "✓ Обновлен"} пользователь: user1')

        user2, created = User.objects.get_or_create(
            username='user2',
            defaults={
                'email': 'user2@example.com',
                'first_name': 'Петр',
                'last_name': 'Петров'
            }
        )
        if created or True:
            user2.set_password('user123')
            user2.save()
            self.stdout.write(f'  {"✓ Создан" if created else "✓ Обновлен"} пользователь: user2')

        self.stdout.write('')

        # Создаем задачи (с get_or_create чтобы избежать дублирования)
        task1, created = Task.objects.get_or_create(
            title='Разработать API',
            creator=admin,
            defaults={
                'description': 'Необходимо разработать REST API для управления задачами с поддержкой JWT аутентификации',
                'assignee': user1,
                'status': TaskStatus.IN_PROGRESS,
                'deadline': timezone.now() + timedelta(days=7)
            }
        )
        if created:
            self.stdout.write(f'  ✓ Создана задача: {task1.title}')

        task2, created = Task.objects.get_or_create(
            title='Написать документацию',
            creator=admin,
            defaults={
                'description': 'Создать подробную документацию API с примерами использования всех endpoints',
                'assignee': user2,
                'status': TaskStatus.NEW,
                'deadline': timezone.now() + timedelta(days=14)
            }
        )
        if created:
            self.stdout.write(f'  ✓ Создана задача: {task2.title}')

        task3, created = Task.objects.get_or_create(
            title='Покрыть тестами',
            creator=user1,
            defaults={
                'description': 'Написать unit-тесты для всех endpoints с покрытием не менее 80%',
                'assignee': user1,
                'status': TaskStatus.REVIEW,
                'deadline': timezone.now() + timedelta(days=5)
            }
        )
        if created:
            self.stdout.write(f'  ✓ Создана задача: {task3.title}')

        self.stdout.write('')

        # Создаем комментарии (только если их еще нет)
        if not Comment.objects.filter(task=task1, author=user1).exists():
            Comment.objects.create(
                task=task1,
                author=user1,
                text='Начал работу над API, уже реализовал базовые endpoints'
            )
            self.stdout.write(f'  ✓ Создан комментарий к задаче: {task1.title}')

        if not Comment.objects.filter(task=task1, author=admin).exists():
            Comment.objects.create(
                task=task1,
                author=admin,
                text='Отлично! Не забудь про валидацию и обработку ошибок'
            )
            self.stdout.write(f'  ✓ Создан комментарий к задаче: {task1.title}')

        if not Comment.objects.filter(task=task3, author=user1).exists():
            Comment.objects.create(
                task=task3,
                author=user1,
                text='Тесты готовы, покрытие 85%. Прошу проверить'
            )
            self.stdout.write(f'  ✓ Создан комментарий к задаче: {task3.title}')

        if not Comment.objects.filter(task=task3, author=admin).exists():
            Comment.objects.create(
                task=task3,
                author=admin,
                text='Проверил, всё отлично! Переводи в Done'
            )
            self.stdout.write(f'  ✓ Создан комментарий к задаче: {task3.title}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('✅ Тестовые данные успешно созданы!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Учетные данные для входа:'))
        self.stdout.write('  • admin / admin123 (суперпользователь)')
        self.stdout.write('  • user1 / user123')
        self.stdout.write('  • user2 / user123')
        self.stdout.write('')
        self.stdout.write('Используйте эти данные для получения JWT токена:')
        self.stdout.write(self.style.HTTP_INFO('  POST http://localhost:8000/api/v1/token/'))
        self.stdout.write('')
