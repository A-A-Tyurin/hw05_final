""" Main url paths for project. """

from django.conf import settings
from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.urls import include, path

handler404 = "posts.views.page_not_found"  # noqa
handler500 = "posts.views.server_error"  # noqa

urlpatterns = [
    path("", include("posts.urls")),
    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path("about/", include("about.urls", namespace='about')),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:

    import debug_toolbar
    from django.conf.urls.static import static

    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )

    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
