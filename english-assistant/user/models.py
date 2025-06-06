from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
import string

from reusable.models import BaseModel


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"({self.pk} {self.user.first_name} {self.user.last_name})"


class OTP(BaseModel):
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email", "otp_code"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"OTP for {self.email} - {self.otp_code}"

    @classmethod
    def generate_otp(cls, email):
        """Generate a new OTP for the given email"""
        # Generate 6-digit OTP
        otp_code = "".join(random.choices(string.digits, k=6))

        # Set expiration time to 3 minutes from now
        expires_at = timezone.now() + timedelta(minutes=3)

        # Invalidate any existing unused OTPs for this email
        cls.objects.filter(email=email, is_used=False).update(is_used=True)

        # Create new OTP
        otp = cls.objects.create(email=email, otp_code=otp_code, expires_at=expires_at)

        return otp

    def is_valid(self):
        """Check if OTP is valid (not used and not expired)"""
        return not self.is_used and timezone.now() <= self.expires_at

    def mark_as_used(self):
        """Mark OTP as used"""
        self.is_used = True
        self.save()
