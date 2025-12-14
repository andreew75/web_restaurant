from django.contrib import admin
from .models import Post, Tag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'is_best')
    list_filter = ('is_published', 'is_best', 'author')
    search_fields = ('title', 'content')


admin.site.register(Tag)

