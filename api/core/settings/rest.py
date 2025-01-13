"""
REST Framework Settings

This module configures Django REST Framework (DRF) and related JWT settings.

JWT Authentication:
- Uses access tokens in the "Authorization" header ("Bearer <token>").
- Suitable for stateless API communication without cookies.
- Requires clients to store and include tokens in the header per request.

JWTCookieAuthentication:
- Uses cookies to store JWT tokens (access and refresh).
- Tokens are automatically sent by browsers via cookies.
- Ideal for web apps; simplifies frontend as browsers handle cookies.

Below, JWTAuthentication is used, requiring tokens in the request header.

DRF Parameters:
- DEFAULT_RENDERER_CLASSES: Renders API responses in standardized format.
  - CustomJSONRenderer: Ensures consistent response structure with code, message
    and data.
  - BrowsableAPIRenderer: Provides a browsable API interface.
- DEFAULT_PARSER_CLASSES: Parses incoming camelCase request data to snake_case.
  - CamelCaseJSONParser: Handles JSON with camelCase keys for internal
    processing.
"""

from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'core.settings.renders.CustomJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# SimpleJWT Settings:
#
# - ACCESS_TOKEN_LIFETIME: Duration for which the access token is valid.
# - REFRESH_TOKEN_LIFETIME: Duration for which the refresh token is valid.
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

# REST Authentication Settings:
#
# - USE_JWT: Enables JWT for authentication.
# - JWT_AUTH_HTTPONLY: Determines if refresh tokens should be HTTP-only.
REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_HTTPONLY": False,
}