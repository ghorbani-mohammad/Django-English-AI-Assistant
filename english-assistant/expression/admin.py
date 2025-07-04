from django.contrib import admin

from . import models
from reusable.admins import ReadOnlyAdminDateFieldsMIXIN


@admin.register(models.Expression)
class ExpressionAdmin(ReadOnlyAdminDateFieldsMIXIN, admin.ModelAdmin):
    list_display = ("pk", "title", "created_at", "updated_at")
    search_fields = ("title",)
    list_filter = ("title",)
