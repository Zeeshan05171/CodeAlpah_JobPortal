from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def api_home(request):
    """Friendly landing view so http://host:port/ doesn't 404 during dev/demo."""
    base = request.build_absolute_uri("/").rstrip("/")
    return JsonResponse({
        "message": "JobPortal API is running.",
        "admin": f"{base}/admin/",
        "api_root": f"{base}/api/",
        "auth": f"{base}/api/auth/",
        "notifications": f"{base}/api/notifications/",
        "note": "The frontend is a separate static site — see frontend/index.html.",
    })


urlpatterns = [
    path("", api_home, name="api-home"),
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("jobs.urls")),
    path("api/notifications/", include("notifications.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "JobPortal Administration"
admin.site.site_title = "JobPortal Admin"
admin.site.index_title = "Dashboard"
