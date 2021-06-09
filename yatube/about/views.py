""" Class based views for 'about' application. """

from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """ TemplateView class for page 'author'. """
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        """
        Override 'get_context_data' to add to the context 'title',
        'description', 'text'.
        """
        context = super().get_context_data(**kwargs)
        params = {
            "title": "Об авторе",
            "description": "Полезный короткий текст об авторе",
            "text": "Текст страницы об авторе"
        }
        context.update(params)
        return context


class AboutTechView(TemplateView):
    """ TemplateView class for page 'technologies'. """
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        """
        Override 'get_context_data' to add to the context 'title',
        'description', 'text'.
        """
        context = super().get_context_data(**kwargs)
        params = {
            "title": "О технологиях",
            "description": "Полезный короткий текст о технологиях",
            "text": "Текст страницы о технологиях"
        }
        context.update(params)
        return context
