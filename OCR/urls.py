
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

from accounts.views import (
    login_view,
    logout_view,
    register_view
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('pdf_gen.urls')),
    path('invoice/', include('api.urls')),
    path('login/', login_view),
    path('logout/', logout_view),
    path('register/', register_view),
]
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
