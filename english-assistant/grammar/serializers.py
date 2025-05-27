from rest_framework import serializers

from . import models


class GrammarSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Grammar
        fields = ["id", "title", "description", "created_at"]
