from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("secret-admin/", admin.site.urls),
    path("api/v1/usr/", include("user.urls")),
    path("api/v1/gra/", include("grammar.urls")),
    path("api/v1/exp/", include("expression.urls")),
]
