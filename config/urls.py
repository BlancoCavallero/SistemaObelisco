"""URL configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.decorators.csrf import ensure_csrf_cookie

from config.views import spa


def health(_request):
    return JsonResponse({"status": "ok", "version": settings.APP_VERSION})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
    path("api/", include("core.urls")),
    path("api/", include("catalogo.urls")),
    path("api/", include("inventario.urls")),
    path("api/", include("ventas.urls")),
    # Everything that is not API, admin, health or a static file belongs to the SPA.
    re_path(r"^(?!api/|admin/|health/|static/|media/).*$", ensure_csrf_cookie(spa), name="spa"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
