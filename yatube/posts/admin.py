""" Admin models for 'posts' application. """

from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):
    """
    Encapsulate admin options and functionality
    for :model:posts.Post.
    """
    list_display = ("text", "pub_date", "author")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    """
    Encapsulate admin options and functionality
    for :model:posts.Group.
    """
    list_display = ("title", "slug")
    search_fields = ("slug",)
    list_filter = ("title",)
    empty_value_display = "-пусто-"


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
