""" Database entry models for 'posts' application. """

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """ Stores a single group entry, related to :model:'posts.Post'. """
    title = models.CharField(
        "Заголовок группы",
        max_length=200,
        help_text="Дайте короткое название группе"
    )
    slug = models.SlugField(
        "Адрес для страницы группы",
        max_length=100,
        unique=True,
        help_text=("Укажите адрес для страницы задачи. Используйте только "
                   "латиницу, цифры, дефисы и знаки подчёркивания")
    )
    description = models.TextField(
        "Описание",
        help_text="Напишите описание группы"
    )

    def __str__(self):
        """ Return group title. """
        return self.title


class Post(models.Model):
    """
    Stores a single post entry, related to :model:'posts.Group'
    and :model:'auth.User'.
    """
    text = models.TextField(
        "Текст",
        help_text="Опишите суть поста"
    )
    pub_date = models.DateTimeField("дата публикации",
                                    auto_now_add=True)

    group = models.ForeignKey(Group, blank=True, null=True,
                              on_delete=models.SET_NULL,
                              related_name="posts")

    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts")

    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        # Posts by descending pub_date.
        ordering = ("-pub_date",)

    def __str__(self):
        """ Return first 15 chars of post's text. """
        return self.text[:15]


class Comment(models.Model):
    """
    Stores a single comment entry, related to :model:'posts.Post'
    and :model:'auth.User'.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="comments")

    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments")

    text = models.TextField(
        "Текст",
        help_text="Опишите суть комментария"
    )

    created = models.DateTimeField("дата публикации",
                                   auto_now_add=True)

    class Meta:
        # Comments by descending pub_date.
        ordering = ("-created",)

    def __str__(self):
        """ Return first 15 chars of comment's text. """
        return self.text[:15]


class Follow(models.Model):
    """
    Stores the relation between :model:'auth.User'
    user as follower and :model:'auth.User' other users as authors.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")

    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")

    def __str__(self):
        """ Return string in format '{user} - {author}'. """
        return f"{self.user} - {self.author}"
