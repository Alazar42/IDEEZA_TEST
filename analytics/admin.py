from django.contrib import admin
from .models import Blog, BlogView

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'country', 'created_at')
    list_filter = ('country', 'created_at')
    search_fields = ('title', 'content', 'author__username')

@admin.register(BlogView)
class BlogViewAdmin(admin.ModelAdmin):
    list_display = ('blog', 'viewer', 'viewer_country', 'viewed_at')
    list_filter = ('viewer_country', 'viewed_at')
    search_fields = ('blog__title', 'viewer__username', 'ip_address')
    date_hierarchy = 'viewed_at'