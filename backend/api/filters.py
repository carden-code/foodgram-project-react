from django_filters import rest_framework as filter

from recipes.models import Ingredient, Recipe, Tag  # isort:skip
from users.models import CustomUser  # isort:skip


class IngredientFilter(filter.FilterSet):
    """
    Класс IngredientFilter для фильтрации списка ингредиентов при
    поиске искомого ингредиента сначала по вхождению в начало
    названия, затем по вхождению в произвольном месте. Результат
    сортируется от первых ко вторым.
    """
    name = filter.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class TagsFilter(filter.FilterSet):
    """
    Класс TagsFilter для фильтрации списка рецептов отмеченными тегам.
    Фильтрация может проводится по нескольким тегам в комбинации «или»:
    если выбраны несколько тегов — в результате должны быть показаны рецепты,
    которые отмечены хотя бы одним из этих тегов. При фильтрации на странице
    пользователя должны фильтроваться только рецепты выбранного пользователя.
    Такой же принцип должен соблюдаться при фильтрации списка избранного.
    """
    tags = filter.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = filter.ModelChoiceFilter(queryset=CustomUser.objects.all())
    is_favorited = filter.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filter.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        """
        Метод `get_is_favorited` для фильтрации рецептов
        списка избранного.
        """
        if value:
            return queryset.filter(favoriterecipe__user=self.request.user)
        return queryset.exclude(favoriterecipe__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        """
        Метод `get_is_in_shopping_cart` для фильтрации рецептов
        спиcка покупок.
        """
        if value:
            return queryset.filter(shoppingcartrecipe__user=self.request.user)
        return queryset.exclude(shoppingcartrecipe__user=self.request.user)
