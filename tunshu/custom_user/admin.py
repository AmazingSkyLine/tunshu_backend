from django.contrib import admin
from custom_user.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ['nickname', 'phone', 'major', 'openid']
    search_fields = ['nickname', 'phone']
    list_filter = ['major']


admin.site.register(User, UserAdmin)
