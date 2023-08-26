from django.core.validators import MinValueValidator
from django.db import models
from colorfield.fields import ColorField

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200,
        unique=True,
    )
    color = ColorField(
        verbose_name='Цвет',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=250,
        db_index=True,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=100,
    )

    class Meta:
        ordering = ('name'),
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_name_measurement_unit'
            ),
        )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/',
        blank=True,
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        db_index=True,
        through='AmountOfIngridients',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        db_index=True,
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                1, 'Время приготовления не должно быть меньше 1 минуты!'
            )
        ]
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class AmountOfIngridients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='amountingridients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='amountingridients'
    )
    amount = models.IntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                1, 'Количество ингредиентов не может быть меньше 1!'
            )
        ]
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe',),
                name='unique_ingredients_recipe'
            ),
        )

    def __str__(self) -> str:
        return f'{self.ingredient} для {self.recipe}'


# class Favorite(models.Model):
#     user = models.ForeignKey(
#         User,
#         verbose_name='Пользователь',
#         on_delete=models.CASCADE,
#         related_name='favorites',
#     )
#     recipe = models.ForeignKey(
#         Recipe,
#         verbose_name='Рецепт',
#         on_delete=models.CASCADE,
#         related_name='favorites',
#     )

#     class Meta:
#         ordering = ['-id']
#         constraints = [
#             models.UniqueConstraint(
#                 fields=('user', 'recipe'),
#                 name='unique_user_favorite'
#             )
#         ]
#         verbose_name = 'Избранное'
#         verbose_name_plural = 'Избранное'

#     def __str__(self):
#         return f'{self.user.username} добавил {self.recipe.name} в избраннное'


# class Cart(models.Model):
#     user = models.ForeignKey(
#         User,
#         verbose_name='Пользователь',
#         on_delete=models.CASCADE,
#         related_name='carts'
#     )
#     recipe = models.ForeignKey(
#         Recipe,
#         verbose_name='Рецепт',
#         on_delete=models.CASCADE,
#         related_name='carts',
#     )

#     class Meta:
#         ordering = ['-id']
#         constraints = [
#             models.UniqueConstraint(
#                 fields=('user', 'recipe'),
#                 name='unique_user_cart'
#             )
#         ]
#         verbose_name = 'Список покупок'
#         verbose_name_plural = 'Списки покупок'

#     def __str__(self):
#         return (f'{self.user.username} добавил'
#                 f'{self.recipe.name} в свой список покупок')


class BaseModelForFavAndCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract=True
        ordering = ['-id']

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.name}'


class Favorite(BaseModelForFavAndCart):
    class Meta(BaseModelForFavAndCart.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_favorite'
            )
        ]


class Cart(BaseModelForFavAndCart):
    class Meta(BaseModelForFavAndCart.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'carts'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_cart'
            )
        ]
