from django_filters import FilterSet, CharFilter, NumberFilter, DateTimeFilter
from .models import Task


class TaskFilter(FilterSet):
    """Фильтр для задач"""
    status = CharFilter(field_name='status', lookup_expr='exact')
    assignee = NumberFilter(field_name='assignee__id', lookup_expr='exact')
    creator = NumberFilter(field_name='creator__id', lookup_expr='exact')
    deadline_from = DateTimeFilter(field_name='deadline', lookup_expr='gte')
    deadline_to = DateTimeFilter(field_name='deadline', lookup_expr='lte')

    class Meta:
        model = Task
        fields = ['status', 'assignee', 'creator', 'deadline_from', 'deadline_to']
