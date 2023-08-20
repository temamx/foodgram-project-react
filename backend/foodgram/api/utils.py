import base64

from rest_framework import status, serializers
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


def post(request, pk, get_object, models, serializer):
    obj = get_object_or_404(get_object, id=pk)
    if models.objects.filter(
        recipe=obj, user=request.user
    ).exists():
        return Response(
            {'message':
                f'Вы уже добавили рецепт {obj}!'},
            status=status.HTTP_400_BAD_REQUEST
        )
    serializer = serializer(
        obj, context={request: 'request'}
    )
    models.objects.create(
        recipe=obj, user=request.user
    )
    return Response(
        serializer.data, status=status.HTTP_201_CREATED
    )


def delete(request, pk, get_object, models):
    obj = get_object_or_404(get_object, id=pk)
    if not models.objects.filter(
        recipe=obj, user=request.user
    ).exists():
        return Response(
            {'message':
                f'Вы не добавляли рецепт {obj}!'}
        )
    models.objects.filter(
        recipe=obj, user=request.user
    ).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
