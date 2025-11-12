from django.contrib import admin
from .models import Task, Comment


class CommentInline(admin.TabularInline):
    """Inline отображение комментариев в задаче"""
    model = Comment
    extra = 0
    fields = ('author', 'text', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = True


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Админка для модели Task"""
    list_display = (
        'id',
        'title',
        'status',
        'creator',
        'assignee',
        'deadline',
        'created_at',
    )
    list_display_links = ('id', 'title')
    list_filter = (
        'status',
        'created_at',
        'deadline',
    )
    search_fields = (
        'title',
        'description',
        'creator__username',
        'assignee__username',
    )
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_select_related = ('creator', 'assignee')
    autocomplete_fields = ('creator', 'assignee')

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'status')
        }),
        ('Участники', {
            'fields': ('creator', 'assignee')
        }),
        ('Сроки', {
            'fields': ('deadline',)
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [CommentInline]

    def get_queryset(self, request):
        """Оптимизация запросов"""
        qs = super().get_queryset(request)
        return qs.select_related('creator', 'assignee').prefetch_related('comments')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админка для модели Comment"""
    list_display = (
        'id',
        'task',
        'author',
        'text_short',
        'created_at',
    )
    list_display_links = ('id', 'text_short')
    list_filter = (
        'created_at',
        'author',
    )
    search_fields = (
        'text',
        'task__title',
        'author__username',
    )
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_select_related = ('task', 'author')
    autocomplete_fields = ('task', 'author')

    fieldsets = (
        ('Основная информация', {
            'fields': ('task', 'author', 'text')
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def text_short(self, obj):
        """Сокращенный текст комментария для списка"""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_short.short_description = 'Текст'

    def get_queryset(self, request):
        """Оптимизация запросов"""
        qs = super().get_queryset(request)
        return qs.select_related('task', 'author')
