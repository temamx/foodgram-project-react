from django.core.validators import MinValueValidator
from django.db import transaction
from django.forms import CharField, EmailField
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from users.models import Follow, User

from api.utils import Base64ImageField
from recipes.models import (
    AmountOfIngridients, Cart, Favorite, Ingredient, Recipe, Tag,
)


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = AmountOfIngridients
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class PostAmountOfIngridientsSerializer(ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                limit_value=1,
                message=('Количество ингредиента не может быть'
                         'меньше 1!')
            ),
        )
    )

    class Meta:
        model = AmountOfIngridients
        fields = ('id', 'amount')


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class RecipeShortInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


# Сериализаторы для пользователя
class CustomUserSerializer(UserSerializer):
    recipes = RecipeShortInfoSerializer(many=True)
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class ReadRecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True, default=serializers.CurrentUserDefault())
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='amountingridients',
        read_only=True
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time',)

    def get_is_favorited(self, obj) -> Favorite:
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj) -> Favorite:
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Cart.objects.filter(user=request.user, recipe=obj).exists()


class WriteRecipeSerializer(ModelSerializer):
    author = CustomUserSerializer(read_only=True, default=serializers.CurrentUserDefault())
    ingredients = PostAmountOfIngridientsSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(
                limit_value=1,
                message=('Время приготовления не может быть '
                         'меньше 1 минуты')
            ),
        )
    )

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time')

    def to_representation(self, instance):
        serializer = ReadRecipeSerializer(instance, context=self.context)
        return serializer.data

    @transaction.atomic
    def create(self, validated_data):
        request = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=request, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            AmountOfIngridients.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        AmountOfIngridients.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        for ingredient in ingredients:
            AmountOfIngridients.objects.create(
                recipe=instance,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        instance.save()
        return instance


class CartSerializer(ModelSerializer):

    class Meta:
        model = Cart
        fields = '__all__'
        validators = (
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок!'
            ),
        )

    def to_representate_an_info(self, instance):
        request = self.context.get('request')
        return RecipeShortInfoSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class FavoriteSerializer(ModelSerializer):

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = (
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже есть в избранном!'
            ),
        )

    def to_representate_an_info(self, instance):
        request = self.context.get('request')
        return RecipeShortInfoSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class CreateUserSerializer(UserCreateSerializer):
    username = CharField(validators=[UniqueValidator(
        queryset=User.objects.all())])
    email = EmailField(validators=[UniqueValidator(
        queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name',
                  'password',)
        extra_kwargs = {'password': {'write_only': True}}


class FollowSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer
    user = CustomUserSerializer

    class Meta:
        model = Follow
        fields = ('author', 'user')
        validators = (
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('author', 'user'),
                message='Вы уже подписаны на данного пользователя!'
            ),
        )

    def validate(self, data):
        author = data.get('author')
        user = data.get('user')
        if user == author:
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на самого себя!'}
            )
        return data

    def create(self, validated_data):
        author = validated_data.get('author')
        user = validated_data.get('user')
        return Follow.objects.create(user=user, author=author)


class RecipesBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ResponseSubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count')

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj) -> dict:
        request = self.context.get('request')
        recipes_limit = request.POST.get('recipes_limit')
        queryset = obj.recipes.all()
        if recipes_limit:
            queryset = queryset[:(recipes_limit)]
        return RecipesBriefSerializer(queryset, many=True).data

    def get_is_subscribed(self, obj) -> Follow:
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()

    def get_recipes_count(self, obj) -> int:
        return obj.recipes.all().count()
