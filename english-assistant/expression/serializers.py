from rest_framework import serializers

from . import models


class ExpressionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Expression
        fields = ["id", "title", "description", "created_at"] 