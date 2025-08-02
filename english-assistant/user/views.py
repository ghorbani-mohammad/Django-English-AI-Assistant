import logging
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTP, Profile
from .serializers import GenerateOTPSerializer, VerifyOTPSerializer, ProfileSerializer
from .tasks import send_template_email_to_user

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([AllowAny])
def generate_otp(request):
    """
    Generate OTP for email authentication.
    Creates user if doesn't exist.

    POST /api/auth/generate-otp/
    {
        "email": "user@example.com"
    }
    """
    serializer = GenerateOTPSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"error": "Invalid data", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = serializer.validated_data["email"]

    try:
        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,  # Use email as username
                "first_name": "",
                "last_name": "",
            },
        )

        # Create profile if user was just created
        if created:
            Profile.objects.create(user=user)
            logger.info(f"New user created with email: {email}")

        # Generate OTP
        otp = OTP.generate_otp(email)

        # Send OTP email (asynchronously using Celery)
        send_template_email_to_user.delay(
            user_id=user.id,
            subject="Your Login OTP Code",
            template_name="otp_email",
            context={
                "otp_code": otp.otp_code,
                "expiry_minutes": 3,
            },
        )

        logger.info(f"OTP generated and email sent for user: {email}")

        return Response(
            {
                "message": "OTP has been sent to your email address",
                "email": email,
                "expires_in_minutes": 3,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Error generating OTP for {email}: {str(e)}")
        return Response(
            {"error": "Failed to generate OTP. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Verify OTP and return JWT tokens.

    POST /api/auth/verify-otp/
    {
        "email": "user@example.com",
        "otp_code": "123456"
    }
    """
    serializer = VerifyOTPSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"error": "Invalid data", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = serializer.validated_data["email"]
    otp_instance = serializer.validated_data["otp_instance"]

    try:
        # Get user
        user = User.objects.get(email=email)

        # Mark OTP as used
        otp_instance.mark_as_used()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        logger.info(f"OTP verified successfully for user: {email}")

        return Response(
            {
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                "tokens": {
                    "access": str(access_token),
                    "refresh": str(refresh),
                },
                "token_info": {
                    "access_token_expires_in_days": 3,
                    "refresh_token_expires_in_days": 10,
                },
            },
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        logger.error(f"User not found for email: {email}")
        return Response(
            {"error": "User not found. Please generate OTP first."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        logger.error(f"Error verifying OTP for {email}: {str(e)}")
        return Response(
            {"error": "Failed to verify OTP. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Get or update user profile.
    
    GET /api/auth/profile/
    PUT /api/auth/profile/
    {
        "timezone": "America/New_York"
    }
    """
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = Profile.objects.create(user=request.user)
    
    if request.method == "GET":
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    
    elif request.method == "PUT":
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer.save()
        logger.info(f"Profile updated for user: {request.user.email}")
        
        return Response(
            {
                "message": "Profile updated successfully",
                "profile": serializer.data
            },
            status=status.HTTP_200_OK,
        )
