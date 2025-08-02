from rest_framework import serializers
from django.contrib.auth.models import User

from .models import OTP, Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model"""
    
    class Meta:
        model = Profile
        fields = ["timezone", "image", "ai_word_count_limit"]
        
    def validate_timezone(self, value):
        """Validate timezone value"""
        # You can add more validation here if needed
        # For now, we'll accept any non-empty string
        if not value or not value.strip():
            raise serializers.ValidationError("Timezone cannot be empty")
        return value.strip()
    
    def validate_ai_word_count_limit(self, value):
        """Validate AI word count limit"""
        if value < 100:
            raise serializers.ValidationError("AI word count limit must be at least 100")
        if value > 10000:
            raise serializers.ValidationError("AI word count limit cannot exceed 10000")
        return value


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
            otp = OTP.objects.get(email=email, otp_code=otp_code, is_used=False)

            if not otp.is_valid():
                raise serializers.ValidationError(
                    "OTP has expired. Please request a new one."
                )

            attrs["otp_instance"] = otp

        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP code or email address.")

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
