from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Task, Comment, TaskStatus


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = fields


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария"""
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'task', 'author', 'text', 'created_at', 'updated_at')
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')

    def create(self, validated_data):
        """Автоматически устанавливаем автора комментария"""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор задачи"""
    creator = UserSerializer(read_only=True)
    assignee = UserSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True
    )
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'status', 'creator', 'assignee',
            'assignee_id', 'deadline', 'created_at', 'updated_at',
            'comments', 'comments_count'
        )
        read_only_fields = ('id', 'creator', 'created_at', 'updated_at')

    def create(self, validated_data):
        """Автоматически устанавливаем создателя задачи"""
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

    def validate_deadline(self, value):
        """Проверка, что дедлайн не в прошлом"""
        if value < timezone.now():
            raise serializers.ValidationError(
                "Срок выполнения не может быть в прошлом"
            )
        return value

    def validate_status(self, value):
        """Проверка корректности перехода между статусами"""
        if self.instance:  # Если это обновление существующей задачи
            old_status = self.instance.status

            # Нельзя вернуть выполненную задачу в статус "Новая"
            if old_status == TaskStatus.DONE and value == TaskStatus.NEW:
                raise serializers.ValidationError(
                    "Нельзя вернуть выполненную задачу в статус 'Новая'"
                )

            # Нельзя перейти из "Новая" сразу в "Выполнено" (пропустив промежуточные этапы)
            if old_status == TaskStatus.NEW and value == TaskStatus.DONE:
                raise serializers.ValidationError(
                    "Нельзя перейти из статуса 'Новая' сразу в 'Выполнено'. "
                    "Сначала переведите задачу в статус 'В работе' или 'На проверке'"
                )

        return value


class TaskListSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для списка задач"""
    creator = UserSerializer(read_only=True)
    assignee = UserSerializer(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'status', 'creator', 'assignee',
            'deadline', 'created_at', 'comments_count'
        )
