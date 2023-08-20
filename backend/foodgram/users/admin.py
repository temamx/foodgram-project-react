from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import Follow, User


class UserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username')
    search_fields = ('username', 'email')
    empty_value_display = '-empty-'


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    search_fields = (
        'author__username',
        'author__email',
        'user__username',
        'user__email',
    )
    empty_value_display = '-empty-'


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
