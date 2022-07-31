from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from backend.settings import (AMOUNT_INGREDIENT, AUTH_USER_MODEL,
                              COOKING_TIME_RECIPE)


class Ingredient(models.Model):
    """
    Класс Ingredient для добавления новых ингредиентов.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """
    Класс Tag для добавления новых тэгов.
    """
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название',
        help_text='Введите название тэга'
    )
    color = ColorField(
        unique=True,
        verbose_name='Цвет в HEX',
        help_text='Выберите цвет'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Уникальный слаг',
        help_text='Введите слаг'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Класс Recipe для добавления новых рецептов.
    """
    author = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        max_length=200,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Введите название рецепта'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        help_text='Загрузите изображение рецепта',
        upload_to='recipes/'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Введите описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты',
        help_text="Добавьте необходимые ингредиенты"
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэг',
        help_text="Добавьте тэги"
    )
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        validators=(MinValueValidator(COOKING_TIME_RECIPE),),
        verbose_name='Время приготовления (в минутах)',
        help_text='Укажите время приготовления (в минутах)'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'name'),
                name='unique_recipe_author'
            ),
        )

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """
    Класс IngredientInRecip для добавления новых ингредиентов в рецепт.
    """
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredientinrecipe',
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredientinrecipe',
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=(MinValueValidator(AMOUNT_INGREDIENT),)
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_ingredientinrecipe'
            ),
        )

    def __str__(self):
        return f'Ингредиент {self.ingredient} в рецепте {self.recipe}'


class Subscription(models.Model):
    """
    Класс Subscription для подписки на авторов рецептов.
    """
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
        )

    def __str__(self):
        return (
            f'Пользователь {self.user} '
            f'подписан на пользователя {self.author}'
        )


class FavoriteList(models.Model):
    """
    Класс FavoriteList для добавления рецептов в избранное.
    """
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favoritelist',
        verbose_name='Подписчик'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favoriterecipe',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Cписок избранного'
        verbose_name_plural = 'Списки избранного'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe'
            ),
        )

    def __str__(self):
        return (
            f'Пользователь {self.user} '
            f'добавил в избранное рецепт: "{self.recipe}"'
        )


class ShoppingCart(models.Model):
    """
    Класс ShoppingCart для добавления рецептов в список покупок.
    """
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shoppingcart',
        verbose_name='Подписчик'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingcartrecipe',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Cписок покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shoppingcart_recipe'
            ),
        )

    def __str__(self):
        return (
            f'Пользователь {self.user} '
            f'добавил в список покупок рецепт: "{self.recipe}"'
        )
