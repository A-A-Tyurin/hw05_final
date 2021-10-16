""" Class based forms for 'users' application. """

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    """ UserCreationForm class for :model:'auth.User'. """

    avatar = forms.ImageField(
        label='Аватарка',
        help_text='Выбирать не обязательно',
        required=False
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()
            _avatar = self.files.get("avatar")
            if _avatar:
                user.profile.avatar = _avatar
                user.profile.save()

        return user
