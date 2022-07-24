from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_(
            'Required. 150 characters or fewer.'
            'Letters, digits and @/./+/-/_ only.'
        ),
        validators=[validators.RegexValidator(regex=r'^[\w.@+-]+\Z')],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    email = models.EmailField(
        _('email'),
        max_length=254,
        unique=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)


    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_following'
            ),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} follows {self.author}'
