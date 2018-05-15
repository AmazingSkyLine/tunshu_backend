from django.contrib import admin
from .models import Notification

# Register your models here.


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'content', 'created')
    search_fields = ('from_user', 'to_user')
    list_filter = ('created', 'from_user', 'to_user')


admin.site.register(Notification, NotificationAdmin)