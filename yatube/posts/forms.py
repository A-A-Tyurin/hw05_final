""" Class based forms for 'posts' application. """

from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    """ModelForm class for :model:'posts.Post'. """
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        labels = {
            "text": "Текст записи",
            "group": "Группа для записи",
            "image": "Картинка для записи"
        }
        help_texts = {
            "group": "Группу выбирать не обязательно.",
            "image": "Картинку выбирать не обязательно.",
        }


class CommentForm(ModelForm):
    """ModelForm class for :model:'posts.Comment'. """
    class Meta:
        model = Comment
        fields = ("text",)
        labels = {
            "text": "Текст комментария",
        }
        help_texts = {
            "text": "Опишите суть комментария",
        }
