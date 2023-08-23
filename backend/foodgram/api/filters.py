from users.models import User
from django_filters.rest_framework import filters, FilterSet
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    author = filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        """
        Пользовательский метод фильтрации для отбора рецептов на основе того,
        добавлены ли они в избранное текущим пользователем.

        Аргументы:
        - queryset (QuerySet): Базовый QuerySet рецептов.
        - name (str): Название поля фильтра.
        - value (bool): Значение, указывающее на необходимость
        фильтрации избранных рецептов или нет.

        Возвращает:
        QuerySet: Отфильтрованный QuerySet рецептов
        в зависимости от статуса избранного.
        """
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """
        Пользовательский метод фильтрации для отбора рецептов на основе того,
        добавлены ли они в корзину покупок текущим пользователем.

        Аргументы:
        - queryset (QuerySet): Базовый QuerySet рецептов.
        - name (str): Название поля фильтра.
        - value (bool): Значение, указывающее на необходимость фильтрации
        рецептов в корзине покупок или нет.

        Возвращает:
        QuerySet: Отфильтрованный QuerySet рецептов
        в зависимости от статуса в корзине покупок.
        """

        if self.request.user.is_authenticated and value:
            return queryset.filter(carts__user=self.request.user)
        return queryset


class IngredientFilter(SearchFilter):
    search_param = 'name'
