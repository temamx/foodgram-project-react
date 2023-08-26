from django_filters.rest_framework import filters, FilterSet
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag
from users.models import User


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


    def apply_filter(self, queryset, filter_name, filter_key, user_check):
        if self.request.user.is_authenticated and user_check:
            filter_parameters = {filter_key: self.request.user}
            return queryset.filter(**filter_parameters)
        return queryset

    def get_is_favorited(self, queryset, name, value):
        return self.apply_filter(queryset, name, "favorites__user", value)

    def get_is_in_shopping_cart(self, queryset, name, value):
        return self.apply_filter(queryset, name, "carts__user", value)


class IngredientFilter(SearchFilter):
    search_param = 'name'
