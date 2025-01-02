"""
Swagger Schema Configuration

This configuration sets up the Swagger schema view for API documentation.
It includes the API's basic information such as title, version, and
description. The schema view is publicly accessible and does not require
authentication.
"""

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="API documentation for API",
        terms_of_service="https://hyperbdr.oneprocloud.com/",
        contact=openapi.Contact(email="xiaoquqi@gmail.com"),
        license=openapi.License(name="License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
    authentication_classes=(),
)
