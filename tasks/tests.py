from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Task, Comment, TaskStatus


class TaskModelTest(TestCase):
    """Тесты модели Task"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )

    def test_create_task(self):
        """Тест создания задачи"""
        task = Task.objects.create(
            title='Тестовая задача',
            description='Описание задачи',
            creator=self.user1,
            assignee=self.user2,
            deadline=timezone.now() + timedelta(days=1)
        )
        self.assertEqual(task.status, TaskStatus.NEW)
        self.assertEqual(task.creator, self.user1)
        self.assertEqual(task.assignee, self.user2)


class TaskAPITest(APITestCase):
    """Тесты API задач"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123'
        )

        # Создаем задачу
        self.task1 = Task.objects.create(
            title='Задача 1',
            description='Описание 1',
            creator=self.user1,
            assignee=self.user1,
            deadline=timezone.now() + timedelta(days=1)
        )

    def test_list_tasks_authenticated(self):
        """Тест получения списка задач авторизованным пользователем"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/v1/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_tasks_unauthenticated(self):
        """Тест получения списка задач неавторизованным пользователем"""
        response = self.client.get('/api/v1/tasks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task(self):
        """Тест создания задачи"""
        self.client.force_authenticate(user=self.user1)
        data = {
            'title': 'Новая задача',
            'description': 'Новое описание',
            'assignee_id': self.user2.id,
            'deadline': (timezone.now() + timedelta(days=2)).isoformat()
        }
        response = self.client.post('/api/v1/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_create_task_with_past_deadline(self):
        """Тест: нельзя создать задачу с дедлайном в прошлом"""
        self.client.force_authenticate(user=self.user1)
        data = {
            'title': 'Задача с прошлым дедлайном',
            'description': 'Описание',
            'deadline': (timezone.now() - timedelta(days=1)).isoformat()
        }
        response = self.client.post('/api/v1/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_see_others_tasks(self):
        """Тест: пользователь не видит чужие задачи"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/api/v1/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_assignee_can_view_task(self):
        """Тест: assignee может просматривать задачу"""
        task = Task.objects.create(
            title='Задача для assignee',
            description='Описание',
            creator=self.user1,
            assignee=self.user2,
            deadline=timezone.now() + timedelta(days=1)
        )
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/api/v1/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_assignee_cannot_update_task(self):
        """Тест: assignee не может изменять задачу (404)"""
        task = Task.objects.create(
            title='Задача',
            description='Описание',
            creator=self.user1,
            assignee=self.user2,
            deadline=timezone.now() + timedelta(days=1)
        )
        self.client.force_authenticate(user=self.user2)
        response = self.client.patch(f'/api/v1/tasks/{task.id}/', {'title': 'Новое название'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_assignee_cannot_delete_task(self):
        """Тест: assignee не может удалять задачу (404)"""
        task = Task.objects.create(
            title='Задача',
            description='Описание',
            creator=self.user1,
            assignee=self.user2,
            deadline=timezone.now() + timedelta(days=1)
        )
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f'/api/v1/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_creator_can_update_task(self):
        """Тест: creator может изменять задачу"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(
            f'/api/v1/tasks/{self.task1.id}/',
            {'title': 'Обновленное название'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, 'Обновленное название')

    def test_complete_task_by_creator(self):
        """Тест: creator может завершить задачу"""
        task = Task.objects.create(
            title='Задача',
            description='Описание',
            creator=self.user1,
            assignee=self.user2,
            status=TaskStatus.REVIEW,
            deadline=timezone.now() + timedelta(days=1)
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f'/api/v1/tasks/{task.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.status, TaskStatus.DONE)

    def test_complete_task_by_assignee_denied(self):
        """Тест: assignee НЕ может завершить задачу (403)"""
        task = Task.objects.create(
            title='Задача',
            description='Описание',
            creator=self.user1,
            assignee=self.user2,
            status=TaskStatus.REVIEW,
            deadline=timezone.now() + timedelta(days=1)
        )
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/v1/tasks/{task.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_transition_new_to_done(self):
        """Тест: нельзя перейти NEW → DONE напрямую"""
        task = Task.objects.create(
            title='Задача',
            description='Описание',
            creator=self.user1,
            status=TaskStatus.NEW,
            deadline=timezone.now() + timedelta(days=1)
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(f'/api/v1/tasks/{task.id}/', {'status': TaskStatus.DONE})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_transition_done_to_new(self):
        """Тест: нельзя вернуть DONE → NEW"""
        task = Task.objects.create(
            title='Задача',
            description='Описание',
            creator=self.user1,
            status=TaskStatus.DONE,
            deadline=timezone.now() + timedelta(days=1)
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(f'/api/v1/tasks/{task.id}/', {'status': TaskStatus.NEW})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CommentAPITest(APITestCase):
    """Тесты API комментариев"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123'
        )

        self.task = Task.objects.create(
            title='Задача',
            description='Описание',
            creator=self.user1,
            assignee=self.user1,
            deadline=timezone.now() + timedelta(days=1)
        )

    def test_create_comment(self):
        """Тест создания комментария"""
        self.client.force_authenticate(user=self.user1)
        data = {
            'task': self.task.id,
            'text': 'Тестовый комментарий'
        }
        response = self.client.post('/api/v1/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)

    def test_user_cannot_comment_on_others_tasks(self):
        """Тест: пользователь не может комментировать чужие задачи"""
        self.client.force_authenticate(user=self.user2)
        data = {
            'task': self.task.id,
            'text': 'Попытка комментария'
        }
        response = self.client.post('/api/v1/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assignee_can_comment(self):
        """Тест: assignee может комментировать задачу"""
        task = Task.objects.create(
            title='Задача',
            description='Описание',
            creator=self.user1,
            assignee=self.user2,
            deadline=timezone.now() + timedelta(days=1)
        )
        self.client.force_authenticate(user=self.user2)
        data = {
            'task': task.id,
            'text': 'Комментарий от assignee'
        }
        response = self.client.post('/api/v1/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_author_can_update_comment(self):
        """Тест: автор может редактировать свой комментарий"""
        comment = Comment.objects.create(
            task=self.task,
            author=self.user1,
            text='Оригинальный текст'
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(
            f'/api/v1/comments/{comment.id}/',
            {'text': 'Обновленный текст'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.text, 'Обновленный текст')

    def test_non_author_cannot_update_comment(self):
        """Тест: не-автор не может редактировать комментарий (404)"""
        task2 = Task.objects.create(
            title='Задача 2',
            description='Описание',
            creator=self.user1,
            assignee=self.user2,
            deadline=timezone.now() + timedelta(days=1)
        )
        comment2 = Comment.objects.create(
            task=task2,
            author=self.user1,
            text='Комментарий'
        )
        self.client.force_authenticate(user=self.user2)
        response = self.client.patch(
            f'/api/v1/comments/{comment2.id}/',
            {'text': 'Попытка изменить'}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_author_can_delete_comment(self):
        """Тест: автор может удалить свой комментарий"""
        comment = Comment.objects.create(
            task=self.task,
            author=self.user1,
            text='Текст'
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/v1/comments/{comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)
