from django.contrib import admin

from users.models import CustomUser  # isort:skip


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """
    Класс CustomUserAdmin для редактирования
    модели CustomUser в интерфейсе админ-зоны.
    """
    list_dispaly = ('__all__',)
    search_fields = ('email', 'username')
