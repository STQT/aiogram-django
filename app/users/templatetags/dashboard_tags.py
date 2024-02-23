from django import template
from datetime import datetime
from django.db.models import Q
from django.core.cache import cache

from app.users.models import TelegramUser

register = template.Library()
CACHE_TIMEOUT = 300


@register.inclusion_tag('admin/dashboard_stats.html')
def get_dashboard_stats():
    cache_key = 'dashboard_stats'
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data
    current_date = datetime.now()
    all_users_in_current_month = TelegramUser.objects.filter(
        Q(created_at__year=current_date.year) &
        Q(created_at__month=current_date.month)
    ).count()
    active_users_in_current_month = TelegramUser.objects.filter(
        Q(created_at__year=current_date.year) &
        Q(created_at__month=current_date.month) & Q(is_active=True)
    ).count()
    all_users = TelegramUser.objects.all().count()
    active_users = TelegramUser.objects.filter(is_active=True).count()
    inactive_users = all_users - active_users

    inactive_users_in_current_month = all_users_in_current_month - active_users_in_current_month

    context = {
        'segment': 'dashboard',
        'all_this_month_users': all_users_in_current_month,
        'active_this_month_users': active_users_in_current_month,
        'inactive_this_month_users': inactive_users_in_current_month,
        'all_users': all_users,
        'active_users': active_users,
        'inactive_users': inactive_users
    }
    cache.set(cache_key, context, CACHE_TIMEOUT)

    return context
