from django.contrib import admin

from . import models
from reusable.admins import ReadOnlyAdminDateFieldsMIXIN


@admin.register(models.Profile)
class ProfileAdmin(ReadOnlyAdminDateFieldsMIXIN, admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "user__first_name",
        "user__last_name",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__first_name", "user__last_name", "user__email")


@admin.register(models.OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ["id", "email", "otp_code", "is_used", "expires_at", "created_at"]
    list_filter = ["is_used", "created_at", "expires_at"]
    search_fields = ["email", "otp_code"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        # Prevent manual OTP creation through admin
        return False

    def has_change_permission(self, request, obj=None):
        # Allow viewing but prevent editing
        return False
