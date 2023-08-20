from django.contrib.auth.models import AbstractUser
from django.db.models import (CASCADE, CharField, EmailField, ForeignKey,
                              Model, UniqueConstraint)


class User(AbstractUser):
    first_name = CharField(
        verbose_name='Имя',
        max_length=50
    )
    last_name = CharField(
        verbose_name='Фамилия',
        max_length=50
    )
    email = EmailField(
        verbose_name='Email',
        unique=True,
        max_length=60
    )
    username = CharField(
        verbose_name='Имя пользователя',
        unique=True,
        max_length=50
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            UniqueConstraint(fields=('username', 'email'),
                             name='unique_user')
        ]

    def __str__(self):
        return self.username


class Follow(Model):
    user = ForeignKey(User,
                      verbose_name='Подписчик',
                      related_name='follower',
                      on_delete=CASCADE)
    author = ForeignKey(User,
                        verbose_name='Автор',
                        related_name='following',
                        on_delete=CASCADE)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            UniqueConstraint(fields=['author', 'user'],
                             name='unique_follower')
        ]

    def __str__(self):
        return f'Автор: {self.author}, подписчик: {self.user}'
