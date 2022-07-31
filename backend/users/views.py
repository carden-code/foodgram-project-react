from rest_framework import viewsets

from users.models import CustomUser  # isort:skip
from users.serializers import CreateCustomUserSerializer  # isort:skip


class UserViewSet(viewsets.ModelViewSet):
    """
    UserViewSet для просмотра и редактирования пользовательских экземпляров.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CreateCustomUserSerializer
    lookup_field = 'username'
