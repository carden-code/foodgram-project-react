from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Класс CustomUser для создания модели пользователя.
    """
    username = models.CharField(max_length=150,
                                unique=True,
                                verbose_name='Логин',
                                help_text='Введите логин'
                                )
    email = models.EmailField(max_length=254,
                              unique=True,
                              verbose_name='Адрес электронной почты',
                              help_text='Введите адрес электронной почты'
                              )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',
                       'password',
                       'first_name',
                       'last_name'
                       ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
