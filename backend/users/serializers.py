from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Subscription  # isort:skip
from users.models import CustomUser  # isort:skip


class CreateCustomUserSerializer(serializers.ModelSerializer):
    """
    Класс CreateCustomUserSerializer для регистрации нового пользователя.
    """
    class Meta:
        model = CustomUser
        fields = ('email',
                  'username',
                  'first_name',
                  'last_name',
                  'password'
                  )

    def create(self, validated_data):
        """
        Метод `create` для создания нового пользователя.
        """
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CurrentCustomUserSerializer(UserSerializer):
    """
    Класс CurrentCustomUserSerializer для получения
    информации о текущем пользователе.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed'
                  )

    def get_is_subscribed(self, obj):
        """
        Метод `get_is_subscribed` для получения информации
        о подписке на автора рецептов.
        """
        request = self.context['request']
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()
