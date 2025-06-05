from rest_framework import serializers
from django.contrib.auth.models import User

from .models import OTP


class GenerateOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """Validate email format"""
        return value.lower()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6, min_length=6)

    def validate_email(self, value):
        """Validate email format"""
        return value.lower()

    def validate_otp_code(self, value):
        """Validate OTP code format"""
        if not value.isdigit():
            raise serializers.ValidationError("OTP code must contain only digits")
        return value

    def validate(self, attrs):
        """Validate OTP existence and validity"""
        email = attrs.get("email")
        otp_code = attrs.get("otp_code")

        try:
            otp = OTP.objects.get(
                email=email,
                otp_code=otp_code,
                is_used=False
            )
            
            if not otp.is_valid():
                raise serializers.ValidationError(
                    "OTP has expired. Please request a new one."
                )
            
            attrs["otp_instance"] = otp
            
        except OTP.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid OTP code or email address."
            )

        return attrs


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]
        extra_kwargs = {
            "email": {"required": True},
        }

    def validate_email(self, value):
        """Validate email format and uniqueness"""
        value = value.lower()
        if User.objects.filter(email=value).exists():
            # If user exists, we don't raise an error here
            # We'll handle it in the view
            pass
        return value 