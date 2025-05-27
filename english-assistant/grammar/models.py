from django.db import models

from reusable.models import BaseModel


class Grammar(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f"({self.pk} - {self.title})"
