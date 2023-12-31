from django import forms

from django.contrib import admin
from django.forms import BaseInlineFormSet

from recipes.models import (Favorite, Ingredient, Recipe,
                            AmountOfIngridients, Cart, Tag)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = '-empty-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')
    empty_value_display = '-empty-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    empty_value_display = '-empty-'


class IngredientsFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        ingredient_count = 0

        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE',
                                                               False):
                ingredient_count += 1
            if ingredient_count < 1:
                raise forms.ValidationError(
                    'Добавьте хотя бы один ингредиент'
                )


class RecipeIngredientInline(admin.TabularInline):
    model = AmountOfIngridients
    formset = IngredientsFormSet


class TagInline(admin.TabularInline):
    model = Recipe.tags.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'favorites_amount')
    search_fields = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-empty-'
    exclude = ('tags',)
    inlines = [
        RecipeIngredientInline, TagInline
    ]

    def favorites_amount(self, obj):
        return obj.favorites.count()


@admin.register(Cart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = '-empty-'


@admin.register(AmountOfIngridients)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    empty_value_display = '-empty-'
