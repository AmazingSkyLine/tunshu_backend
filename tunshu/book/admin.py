from django.contrib import admin
from book.models import Book, Category


class BookAdmin(admin.ModelAdmin):
    list_display = ['name', 'created']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


admin.site.register(Book, BookAdmin)
admin.site.register(Category, CategoryAdmin)
