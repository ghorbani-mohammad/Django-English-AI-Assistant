from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = "user"

urlpatterns = [
    # OTP Authentication endpoints
    path("auth/generate-otp/", views.generate_otp, name="generate_otp"),
    path("auth/verify-otp/", views.verify_otp, name="verify_otp"),
    # JWT Token refresh endpoint
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Profile management endpoint
    path("auth/profile/", views.profile_view, name="profile"),
]
