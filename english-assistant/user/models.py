from django.db import models
from django.contrib.auth.models import User

from reusable.models import BaseModel


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"({self.pk} {self.user.first_name} {self.user.last_name})"
