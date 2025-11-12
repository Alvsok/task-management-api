from django.db import models
from django.contrib.auth.models import User


class TaskStatus(models.TextChoices):
    """Статусы задачи"""
    NEW = 'new', 'Новая'
    IN_PROGRESS = 'in_progress', 'В работе'
    REVIEW = 'review', 'На проверке'
    DONE = 'done', 'Выполнено'


class Task(models.Model):
    """Модель задачи"""
    title = models.CharField('Название', max_length=255)
    description = models.TextField('Описание')
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.NEW
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        verbose_name='Создатель'
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='Исполнитель'
    )
    deadline = models.DateTimeField('Срок выполнения')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['assignee', 'status']),
            models.Index(fields=['creator']),
            models.Index(fields=['deadline']),
        ]

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Модель комментария к задаче"""
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Задача'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField('Текст комментария')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f'Комментарий от {self.author.username} к задаче {self.task.title}'
