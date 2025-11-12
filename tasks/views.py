from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count

from .models import Task, Comment, TaskStatus
from .serializers import (
    TaskSerializer, TaskListSerializer, CommentSerializer
)
from .filters import TaskFilter


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet для управления задачами"""
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'deadline', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Пользователь видит задачи, где он исполнитель или создатель.
        Изменять/удалять может только создатель.
        """
        user = self.request.user
        qs = Task.objects.filter(
            Q(assignee=user) | Q(creator=user)
        )

        # Для изменения/удаления - только задачи, где user = creator
        if self.action in ['update', 'partial_update', 'destroy']:
            qs = qs.filter(creator=user)

        return qs.select_related('creator', 'assignee') \
                 .prefetch_related('comments') \
                 .annotate(comments_count=Count('comments'))

    def get_serializer_class(self):
        """Использовать разные сериализаторы для списка и детали"""
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Отметить задачу как выполненную (только создатель)"""
        task = self.get_object()

        # Только создатель может отметить задачу как выполненную
        if task.creator != request.user:
            raise PermissionDenied(
                "Только создатель задачи может отметить её как выполненную"
            )

        task.status = TaskStatus.DONE
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для управления комментариями"""
    serializer_class = CommentSerializer

    def get_queryset(self):
        """
        Пользователь видит комментарии только к своим задачам.
        Изменять/удалять может только автор комментария.
        """
        user = self.request.user
        qs = Comment.objects.filter(
            Q(task__assignee=user) | Q(task__creator=user)
        )

        # Для изменения/удаления - только комментарии, где user = author
        if self.action in ['update', 'partial_update', 'destroy']:
            qs = qs.filter(author=user)

        return qs.select_related('author', 'task')

    def perform_create(self, serializer):
        """Проверка доступа к задаче перед созданием комментария"""
        task = serializer.validated_data['task']
        user = self.request.user

        # Проверяем, что пользователь имеет доступ к задаче
        if task.assignee != user and task.creator != user:
            raise PermissionDenied(
                "У вас нет доступа к этой задаче"
            )

        serializer.save(author=user)
