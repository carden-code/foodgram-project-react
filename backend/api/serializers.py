from django.core.validators import MinValueValidator
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (FavoriteList, Ingredient,  # isort:skip
                            IngredientInRecipe, Recipe,
                            ShoppingCart, Subscription, Tag)
from rest_framework import serializers  # isort:skip
from rest_framework.validators import UniqueTogetherValidator  # isort:skip
from users.models import CustomUser  # isort:skip
from users.serializers import CurrentCustomUserSerializer  # isort:skip

from backend.settings import (AMOUNT_INGREDIENT,  # isort:skip
                              COOKING_TIME_RECIPE)


class AuthorSerializer(serializers.ModelSerializer):
    """
    Сериализатор AuthorSerializer для модели CustomUser.
    """
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

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
        Метод `get_is_subscribed` проверяет подписку
        пользователя на автора рецептов.
        """
        request = self.context['request']
        user = request.user
        if request is None or request.user.is_anonymous:
            return False
        return user.follower.filter(author=obj).exists()


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор IngredientSerializer для модели Ingredient.
    """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')

    def create(self, validated_data):
        """
        Метод `create` для создания нового ингредиента.
        """
        return Ingredient.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Метод `update` для редактирования ингредиента.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.measurement_unit = validated_data.get(
            'measurement_unit',
            instance.measurement_unit
        )
        instance.save()
        return instance

    def to_internal_value(self, data):
        """
        Метод `to_internal_value` возвращает валидированные данные.
        """
        return get_object_or_404(Ingredient, id=data)


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор IngredientInRecipeSerializer для модели IngredientInRecipe.
    """
    id = IngredientSerializer()
    name = serializers.CharField(required=False)
    measurement_unit = serializers.CharField(required=False)
    amount = serializers.IntegerField(
        validators=(MinValueValidator(AMOUNT_INGREDIENT),)
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'amount', 'measurement_unit')

    def to_representation(self, instance):
        """
        Метод `to_representation` возвращает представление.
        """
        data = IngredientSerializer(instance.ingredient).data
        data['amount'] = instance.amount
        return data


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор TagSerializer для модели Tag.
    """
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag

    def create(self, validated_data):
        """
        Метод `create` для создания нового тэга.
        """
        return Tag.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Метод `update` для редактирования тэга.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.color = validated_data.get('color', instance.color)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.save()
        return instance

    def to_internal_value(self, data):
        """
        Метод `to_internal_value` возвращает валидированные данные.
        """
        return Tag.objects.get(id=data)


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор RecipeSerializer для модели Recipe.
    """
    tags = TagSerializer(many=True)
    author = AuthorSerializer(default=CurrentCustomUserSerializer())
    ingredients = IngredientInRecipeSerializer(
        source='ingredientinrecipe',
        many=True
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )
    image = Base64ImageField(required=False)
    cooking_time = serializers.IntegerField(
        validators=(MinValueValidator(COOKING_TIME_RECIPE),)
    )

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time'
                  )
        validators = (
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'author')
            ),
        )

    def get_is_favorited(self, obj):
        """
        Метод `get_is_favorited` проверяет
        наличие рецепта в избранном.
        """
        request = self.context['request']
        if request is None or request.user.is_anonymous:
            return False
        return FavoriteList.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """
        Метод `get_is_in_shopping_cart` проверяет
        наличие рецепта в списке покупок.
        """
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        if ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists():
            return True
        return False

    @transaction.atomic
    def create(self, validated_data):
        """
        Метод `create` создает новый рецепт.
        """
        ingredients = validated_data.pop('ingredientinrecipe')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0!'
                )
            IngredientInRecipe.objects.create(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount'])
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Метод `update` редактирует рецепт.
        """
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientinrecipe')
        instance.tags.set(tags)
        Recipe.objects.filter(pk=instance.pk).update(**validated_data)
        for ingredient in ingredients:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0!'
                )
            IngredientInRecipe.objects.create(
                ingredient=ingredient['id'],
                recipe=instance,
                amount=ingredient['amount'],
            )
        instance.refresh_from_db()
        return instance


class SubscriptionRecipesSerializer(RecipeSerializer):
    """
    Сериализатор SubscriptionRecipesSerializer для модели Recipe.
    (короткий рецепт).
    """
    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time'
                  )


class SubscribtionSerializer(serializers.ModelSerializer):
    """
    Сериализатор SubscribtionSerializer для модели Subscribtion.
    """
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        model = Subscription

    def get_is_subscribed(self, obj):
        """
        Метод `get_is_subscribed` проверяет подписку на автора рецепта.
        """
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        """
        Метод `get_recipes` получет список рецептов автора.
        """
        request = self.context['request']
        if request.GET.get('recipes_limit'):
            recipes_limit = int(request.GET.get('recipes_limit'))
            queryset = Recipe.objects.filter(
                author=obj.author)[:recipes_limit]
        else:
            queryset = Recipe.objects.filter(
                author=obj.author)
        return SubscriptionRecipesSerializer(
            queryset, many=True
        ).data

    def get_recipes_count(self, obj):
        """
        Метод `get_recipes_count` получет общее количество
        рецептов автора.
        """
        return obj.author.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('id', 'user', 'author')
        validators = (
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author')
            ),
        )

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        serializer = SubscribtionSerializer(
            instance,
            context=context
        )
        return serializer.data

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя!')
        return data
