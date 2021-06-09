""" Decorators for applications in project. """

from functools import wraps

from django.shortcuts import redirect


def author_required(func):
    """
    Decorator for post edit view that checks that the user is
    the post author.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        post_id = kwargs.get("post_id")
        username = kwargs.get("username")
        if request.user.posts.filter(id=post_id).exists():
            return func(request, *args, **kwargs)
        return redirect("post", username, post_id)
    return wrapper


def login_required_for_page(reverse_address_list=None):
    """
    Decorator for views that checks that the user is
    authenticated for the specified page.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.path not in reverse_address_list:
                return func(request, *args, **kwargs)

            if request.user.is_authenticated:
                return func(request, *args, **kwargs)

            return redirect("login")
        return wrapper
    return decorator
