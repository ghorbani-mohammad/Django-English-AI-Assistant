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
