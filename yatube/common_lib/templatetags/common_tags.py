""" Custom template tags for applications in project. """

from django import template

register = template.Library()


@register.filter(name="addclass")
def addclass(field, css):
    """ Custom template tag that add input css attribute to html tag. """
    return field.as_widget(attrs={"class": css})
