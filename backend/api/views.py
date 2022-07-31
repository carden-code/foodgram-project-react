from http import HTTPStatus

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, TagsFilter  # isort:skip
from api.pagination import RecipePagination  # isort:skip
from api.permissions import AuthorOrReadOnly  # isort:skip
from api.serializers import (IngredientSerializer,  # isort:skip
                             RecipeSerializer, SubscribeSerializer,
                             SubscribtionSerializer,
                             SubscriptionRecipesSerializer, TagSerializer)
from api.util import shopping_cart_pdf  # isort:skip
from backend.settings import FILENAME  # isort:skip
from recipes.models import (FavoriteList, Ingredient,  # isort:skip
                            IngredientInRecipe, Recipe,
                            ShoppingCart, Subscription, Tag)
from users.models import CustomUser  # isort:skip


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для отображения списка или одного ингредиента.
    """
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для отображения списка или одного тега.
    """
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для отображения списка или одного рецепта,
    редактирования, обновления и удаления рецепта. Для
    добавления или удаления рецепта в избранное или список покупок.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = RecipePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TagsFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """
        Метод `favorite` вызывает метод добавления или удаления рецепта
        из списка избранного.
        """
        if request.method == 'POST':
            return self.add_recipe(FavoriteList, request, pk)
        else:
            return self.delete_recipe(FavoriteList, request, pk)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """
        Метод `shopping_cart` вызывает метод добавления или удаления рецепта
        из списка покупок.
        """
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request, pk)
        else:
            return self.delete_recipe(ShoppingCart, request, pk)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """
        Метод `download_shopping_cart` выгружает pdf-файл
        с перечнем и количеством необходимых ингредиентов
        для рецептов из "Списка покупок".
        """
        result = IngredientInRecipe.objects.filter(
            recipe__shoppingcartrecipe__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(
            ingredient_total=Sum('amount')
        )
        file = shopping_cart_pdf(result)
        return FileResponse(
            file,
            content_type='application/pdf',
            as_attachment=True,
            filename=FILENAME,
            status=HTTPStatus.OK
        )

    def add_recipe(self, model, request, pk):
        """
        Метод `add_recipe` добавляет рецепт
        в список избранного или список покупок.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(recipe=recipe, user=request.user).exists():
            return Response(status=HTTPStatus.BAD_REQUEST)
        model.objects.create(recipe=recipe, user=request.user)
        serializer = SubscriptionRecipesSerializer(recipe)
        return Response(data=serializer.data, status=HTTPStatus.CREATED)

    def delete_recipe(self, model, request, pk):
        """
        Метод `delete_recipe` удаляет рецепт
        из списка избранного или списка покупок.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            model.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(status=HTTPStatus.BAD_REQUEST)


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для отображения списка подписок пользователя.
    """
    serializer_class = SubscribtionSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = RecipePagination

    def get_queryset(self):
        user = self.request.user
        return Subscription.objects.filter(user=user)


class SubscribeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для создания или удаления подписки на автора рецепта.
    """
    permission_classes = (IsAuthenticated,)

    def create(self, request, id):
        """
        Метод `create` создает подписку на автора.
        """
        author = get_object_or_404(CustomUser, id=id)
        user = self.request.user
        data = {'author': author.id, 'user': user.id}
        serializer = SubscribeSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=HTTPStatus.CREATED)

    def delete(self, request, id):
        """
        Метод `delete` удаляет подписку на автора.
        """
        author = get_object_or_404(CustomUser, id=id)
        user = self.request.user
        subscription = get_object_or_404(
            Subscription, user=user, author=author
        )
        subscription.delete()
        return Response(status=HTTPStatus.NO_CONTENT)
