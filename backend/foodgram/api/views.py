from django.db.models import Sum
from api.pagination import Pagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import HttpResponse, get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from djoser.views import UserViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CartSerializer, FavoriteSerializer,
                             FollowSerializer, IngredientSerializer,
                             ReadRecipeSerializer,
                             ResponseSubscribeSerializer,
                             TagSerializer, WriteRecipeSerializer,
                             )
from api.utils import post, delete
from recipes.models import (Favorite, Ingredient, Recipe,
                            AmountOfIngridients, Cart, Tag)
from users.models import Follow, User


class CustomUserViewSet(UserViewSet):
    pagination_class = Pagination

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        serializer = FollowSerializer(
            data={'user': user.id, 'author': author.id}
        )
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = ResponseSubscribeSerializer(
                author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        follow = Follow.objects.filter(user=user, author=author)
        if not follow.exists():
            return Response(
                {'errors': 'Данный пользователь в ваших подписках не найден!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('GET',),
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = ResponseSubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (IngredientFilter,)
    search_fields = ('name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return post(request, pk, Recipe, Favorite, FavoriteSerializer)

        if request.method == 'DELETE':
            return delete(request, pk, Recipe, Favorite)

        return HttpResponse(status=400)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return post(request, pk, Recipe, Cart, CartSerializer)

        if request.method == 'DELETE':
            return delete(request, pk, Recipe, Cart)

        return HttpResponse(status=400)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        ingredients = AmountOfIngridients.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.txt"'
        return response
