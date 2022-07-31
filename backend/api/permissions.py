from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):
    """
    Класс AuthorOrReadOnly определяет разрешения на уровне объекта.
    """
    def has_permission(self, request, view):
        """
        Метод `has_permission` определяет разрешен ли
        запрос и имеет ли пользователь доступ к
        определенному представлению.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """
        Метод `has_object_permission` определяет
        разрешено ли конкретному пользователю
        взаимодействовать с определенным объектом.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
