from django import forms
from django.contrib import admin

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


class RecipeIngredientInline(admin.TabularInline):
    model = AmountOfIngridients
    min_num = 1


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


class CustomRecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'


MyFormSet = forms.formset_factory(CustomRecipeForm)


class CustomFormSet(MyFormSet):

    def ingredients(self, obj):
        return list(obj.ingredients.all())

    def clean(self):
        cleaned_data = super().clean()
        if self.ingredients() < 1:
            raise forms.ValidationError(
                'Нужно добавить хотя бы один ингредиент'
            )
        return cleaned_data


admin.site.register(CustomFormSet)


@admin.register(Cart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    empty_value_display = '-empty-'


@admin.register(AmountOfIngridients)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    empty_value_display = '-empty-'
