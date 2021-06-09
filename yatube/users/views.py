""" Class based views for 'users' application. """

from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    """ CreateView class for :model:'auth.User'. """
    form_class = CreationForm
    success_url = reverse_lazy("login")
    template_name = "signup.html"
