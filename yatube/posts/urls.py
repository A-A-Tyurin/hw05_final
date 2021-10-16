""" Url pathes for 'posts' application. """

from django.urls import path

from .views import add_comment, profile_follow, profile_unfollow
from .views import PostDetailView as PostDetail
from .views import PostFormCreateView as PostCreate
from .views import PostFormUpdateView as PostUpdate
from .views import PostsListView as PostsList

urlpatterns = [
    path("", PostsList.as_view(), name="index"),
    path("new/", PostCreate.as_view(), name="post_new"),
    path("follow/", PostsList.as_view(), name="follow_index"),
    path("group/<slug:slug>/", PostsList.as_view(), name="group"),
    path("<str:username>/", PostsList.as_view(), name="profile"),
    path("<str:username>/follow/", profile_follow, name="profile_follow"),
    path("<str:username>/unfollow/", profile_unfollow,
         name="profile_unfollow"),
    path("<str:username>/<int:post_id>/", PostDetail.as_view(), name="post"),
    path("<str:username>/<int:post_id>/edit/", PostUpdate.as_view(),
         name="post_edit"),
    path("<str:username>/<int:post_id>/comment", add_comment,
         name="add_comment"),
]
