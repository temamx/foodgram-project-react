import base64

from rest_framework import status, serializers
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile

from recipes.models import Recipe


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


def post(self, user, pk, model):
    obj = get_object_or_404(Recipe, id=pk)
    if model.objects.filter(
        recipe__id=pk, user=user
    ).exists():
        return Response(
            {'message':
                f'Вы уже добавили рецепт {obj}!'},
            status=status.HTTP_400_BAD_REQUEST
        )
    serializer = serializers(obj)
    model.objects.create(
        recipe__id=pk, user=user
    )
    return Response(
        serializer.data, status=status.HTTP_201_CREATED
    )


def delete(self, user, pk, model):
    obj = model.objects.filter(recipe__id=pk, user=user)
    if obj().exists():
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        {'message':
        f'Вы не добавляли рецепт {obj}!'}
        )
