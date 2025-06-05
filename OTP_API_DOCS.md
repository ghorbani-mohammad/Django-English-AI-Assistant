# OTP-Based Authentication API

This document describes the OTP (One-Time Password) authentication system implemented for the English Assistant application.

## Overview

The authentication system uses email-based OTP verification with JWT tokens for secure access. Users receive a 6-digit OTP code via email that expires in 3 minutes.

## Features

- Email-based OTP authentication
- Automatic user creation if email doesn't exist
- JWT access tokens (valid for 3 days)
- JWT refresh tokens (valid for 10 days)
- Automatic OTP cleanup for expired codes
- Email templates with professional styling

## API Endpoints

### 1. Generate OTP

**POST** `/api/v1/auth/generate-otp/`

Generates and sends an OTP code to the specified email address. If the user doesn't exist, it will be created automatically.

#### Request Body
```json
{
    "email": "user@example.com"
}
```

#### Response (Success - 200)
```json
{
    "message": "OTP has been sent to your email address",
    "email": "user@example.com",
    "expires_in_minutes": 3
}
```

#### Response (Error - 400)
```json
{
    "error": "Invalid data",
    "details": {
        "email": ["Enter a valid email address."]
    }
}
```

### 2. Verify OTP

**POST** `/api/v1/auth/verify-otp/`

Verifies the OTP code and returns JWT access and refresh tokens.

#### Request Body
```json
{
    "email": "user@example.com",
    "otp_code": "123456"
}
```

#### Response (Success - 200)
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "tokens": {
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    },
    "token_info": {
        "access_token_expires_in_days": 3,
        "refresh_token_expires_in_days": 10
    }
}
```

#### Response (Error - 400)
```json
{
    "error": "Invalid data",
    "details": {
        "non_field_errors": ["OTP has expired. Please request a new one."]
    }
}
```

### 3. Refresh Token

**POST** `/api/v1/auth/token/refresh/`

Refreshes the access token using a valid refresh token.

#### Request Body
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Response (Success - 200)
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Authentication

For protected endpoints, include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Security Features

1. **OTP Expiration**: OTPs expire after 3 minutes
2. **Single Use**: Each OTP can only be used once
3. **Automatic Cleanup**: Expired OTPs are automatically invalidated
4. **Token Rotation**: Refresh tokens are rotated on use
5. **Email Validation**: Comprehensive email format validation

## Database Models

### OTP Model
- `email`: EmailField - User's email address
- `otp_code`: CharField(6) - 6-digit numeric code
- `expires_at`: DateTimeField - Expiration timestamp
- `is_used`: BooleanField - Whether OTP has been used
- `created_at`: DateTimeField - Creation timestamp

## Management Commands

### Clean up expired OTPs
```bash
python manage.py cleanup_expired_otps
```

### Dry run to see what would be deleted
```bash
python manage.py cleanup_expired_otps --dry-run
```

## Email Template

The system uses a professional HTML email template (`templates/emails/otp_email.html`) that includes:
- Branded header with English Assistant logo
- Clear OTP code display
- Security warnings and best practices
- Responsive design
- Professional styling

## Error Handling

The API includes comprehensive error handling for:
- Invalid email formats
- Expired OTPs
- Used OTPs
- Non-existent users
- Network/email sending failures
- Invalid token formats

## Installation and Setup

1. Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Configure email settings in your environment variables:
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`

4. Start Celery worker for background email tasks:
```bash
celery -A english-assistant worker --loglevel=info
```

5. (Optional) Set up periodic cleanup of expired OTPs using Celery Beat or cron jobs.

## Testing the API

You can test the API using tools like:
- Postman
- curl
- HTTPie
- Any REST client

Example with curl:

```bash
# Generate OTP
curl -X POST http://localhost:8000/api/v1/auth/generate-otp/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Verify OTP
curl -X POST http://localhost:8000/api/v1/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "otp_code": "123456"}'
``` 