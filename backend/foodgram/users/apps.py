from django.apps import AppConfig


class UsersConfig(AppConfig):
    verbose_name = 'Пользователи и подписки'
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'