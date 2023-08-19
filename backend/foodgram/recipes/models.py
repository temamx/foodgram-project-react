from django.core.validators import MinValueValidator
from django.db import models
from backend.foodgram.recipes.admin import IngredientAdmin

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200,
        unique=True
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=7,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=200,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

class Recipе(models.Model):
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
        IngredientAdmin,
        verbose_name='Ингредиенты',
        db_index=True,
        through='RecipeIngredient',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        db_index=True
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

class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=250,
        db_index=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=100,
    )

    class Meta:
        ordering=['name'],
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name

class AmountOfIngridients(models.Model):
    recipe = models.ForeignKey(
        Recipе,
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


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipе,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorites',
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_favorite'
            )
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.name} в избраннное'


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='carts'
    )
    recipe = models.ForeignKey(
        Recipе,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='carts',
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_cart'
            )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return (f'{self.user.username} добавил'
                f'{self.recipe.name} в свой список покупок')
