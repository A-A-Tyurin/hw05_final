""" Class based views for 'posts' application. """

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models.query import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, CreateView, UpdateView, ListView

from common_lib.decorators import author_required, login_required_for_page
from yatube.settings import PAGINATOR_PAGE_SIZE

from .forms import PostForm, CommentForm
from .models import Group, Post, Comment

User = get_user_model()


@method_decorator(login_required_for_page(
    reverse_address_list=[
        reverse_lazy("follow_index"),
    ]),
    name="dispatch"
)
class PostsListView(ListView):
    """ ListView class for :model:'posts.Post'. """
    template_name = "posts_view.html"
    paginate_by = PAGINATOR_PAGE_SIZE
    context_object_name = "posts"

    def get_queryset(self):
        """
        Override 'get_queryset' to get the list depending on the url parameters
        - If no parameters, take all posts
        - If there is a slug, take posts filtered by group
        - If there is a username, take posts filtered by user
        """
        postsManager = (
            Post.objects.select_related("author", "group")
                        .prefetch_related(
                            Prefetch(
                                "comments",
                                queryset=Comment.objects
                                                .select_related("author")
                                                .only(
                                                    "id", "post_id", "text",
                                                    "created", "author__id",
                                                    "author__username"
                                                )))
                        .only("id", "text", "pub_date", "group_id",
                              "author_id", "image", "group__id",
                              "group__title", "group__slug", "author__id",
                              "author__username")
        )

        # process Group page request
        if self.kwargs.get("slug"):
            slug = self.kwargs.get("slug")
            return postsManager.filter(group__slug=slug)

        # process Author page request
        if self.kwargs.get("username"):
            username = self.kwargs.get("username")
            return postsManager.filter(author__username=username)

        # process Follow page request
        if self.request.path == reverse_lazy("follow_index"):
            return postsManager.filter(
                author__following__user=self.request.user
            )

        # process Index page request
        return postsManager

    def get_context_data(self, **kwargs):
        """
        Override 'get_context_data' to add data to the context
        depending on the parameters
        - If there is a slug, add group :model:'posts.Group' to the context
        - If there is a username, add author :model:'auth.User' to the context
        """
        data = super().get_context_data(**kwargs)
        data["page"] = data.pop("page_obj")  # hot fix for paginator tests :)

        # process Group page request
        if self.kwargs.get("slug"):
            slug = self.kwargs.get("slug")
            data.update({"group": get_object_or_404(Group, slug=slug)})
            return data

        # process Author page request
        if self.kwargs.get("username"):
            username = self.kwargs.get("username")
            author = get_object_or_404(
                User.objects.only("username", "first_name", "last_name"),
                username=username
            )
            params = {
                "author": author,
                "user_is_follower": (self.request.user.is_authenticated
                                     and author.following
                                               .filter(user=self.request.user)
                                               .exists())
            }
            data.update(params)
            return data

        # process Index page request
        return data


class PostDetailView(DetailView):
    """ DetailView class for :model:'posts.Post'. """
    template_name = "post_view.html"
    context_object_name = "post"
    pk_url_kwarg = "post_id"

    def get_queryset(self):
        """
        Override 'get_queryset' to get the object depending on
        :model:'posts.Post' id and :model:'auth.User' username parameters
        """
        username = self.kwargs.get("username")
        return (Post.objects
                    .select_related("author", "group")
                    .prefetch_related(
                        Prefetch(
                            "comments",
                            queryset=Comment.objects
                                            .select_related("author")
                                            .only(
                                                "id", "post_id", "text",
                                                "created", "author__id",
                                                "author__username"
                                            )))
                    .only("id", "text", "pub_date", "group_id",
                          "author_id", "image", "group__id",
                          "group__title", "group__slug", "author__id",
                          "author__username", "author__first_name",
                          "author__last_name")
                    .filter(author__username=username))

    def get_context_data(self, **kwargs):
        """
        Override 'get_context_data' to add :model:'forms.CommentForm
        to the context
        """
        data = super().get_context_data(**kwargs)
        user_is_follower = (
            self.request.user.is_authenticated
            and self.request.user.follower.filter(
                author__username=self.kwargs.get("username")
            )
        )

        params = {
            "comment_form": CommentForm(),
            "user_is_follower": user_is_follower
        }
        data.update(params)
        return data


@method_decorator(login_required, name="dispatch")
class PostFormCreateView(CreateView):
    """ CreateView class for :model:'posts.Post'. """
    form_class = PostForm
    template_name = "post_form.html"

    def form_valid(self, form):
        """
        Override 'form_valid' to set the relation to
        :model:'auth.User' author.
        """
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return redirect(reverse_lazy("index"))


@method_decorator([login_required, author_required], name="dispatch")
class PostFormUpdateView(UpdateView):
    """ UpdateView class for :model:'posts.Post'. """
    form_class = PostForm
    template_name = "post_form.html"
    pk_url_kwarg = "post_id"

    def get_queryset(self):
        """
        Override 'get_queryset' to get the object depending on
        :model:'posts.Post' id and :model:'auth.User' username parameters
        """
        username = self.kwargs.get("username")
        return (Post.objects.filter(author__username=username))

    def get_success_url(self):
        """
        Override 'get_success_url' to get the url depending on
        :model:'posts.Post' id and :model:'auth.User' username parameters
        """
        return reverse_lazy("post", kwargs=self.kwargs)


@login_required
def add_comment(request, **kwargs):
    form = CommentForm(request.POST or None)

    if form.is_valid():
        post_username = kwargs.get("username")
        post_id = kwargs.get("post_id")
        post = get_object_or_404(
            Post, id=post_id, author__username=post_username
        )

        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect(reverse_lazy("post", kwargs=kwargs))


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)

    is_following = author.following.filter(user=request.user).exists()

    if author != request.user and not is_following:
        author.following.create(user=request.user, author=author)

    return redirect("profile", username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    following = author.following.filter(user=request.user)

    if following.exists():
        following.delete()

    return redirect("profile", username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
