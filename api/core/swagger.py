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
from rest_framework.serializers import (IntegerField,
                                        CharField,
                                        FloatField,
                                        DateTimeField)
from rest_framework_simplejwt.authentication import JWTAuthentication

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="API documentation for API",
        terms_of_service="https://mito.sunqi.site/",
        contact=openapi.Contact(email="xiaoquqi@gmail.com"),
        license=openapi.License(name="License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
    authentication_classes=(),
)

def get_page_parameters():
    """
    Generate OpenAPI parameters for pagination.

    Returns a list of page and page_size parameters for use in @swagger_auto_schema
    decorators to document paginated API endpoints.

    Can be used in any app's views.py to display pagination parameters in Swagger.

    Example:
        @swagger_auto_schema(
            manual_parameters=get_page_parameters(),
            responses={200: response_schema}
        )
        def get(self, request):
            ...
    """
    return [
        openapi.Parameter(
            'page',
            openapi.IN_QUERY,
            description="Page number",
            type=openapi.TYPE_INTEGER,
            default=1
        ),
        openapi.Parameter(
            'page_size',
            openapi.IN_QUERY,
            description="Number of items per page",
            type=openapi.TYPE_INTEGER,
            default=10
        )
    ]

def get_list_response_schema(item_schema):
    """
    Generate OpenAPI schema for non-paginated list responses.

    Takes a serializer class or schema for list items and returns a schema
    describing the response format for a list of items.

    Args:
        item_schema: Serializer class or OpenAPI Schema for list items

    Example:
        @swagger_auto_schema(
            responses={
                200: get_list_response_schema(PostSerializer)
            }
        )
        def get(self, request):
            ...
    """
    return openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=get_serializer_schema(item_schema),
        description="List of items"
    )

def get_pagination_schema(item_schema):
    """
    Generate OpenAPI schema for paginated responses.

    Takes a serializer class or schema for list items and returns a schema
    describing paginated response format with count, next/prev links and results.

    Args:
        item_schema: Serializer class or OpenAPI Schema for list items

    Example:
        schema = get_pagination_schema(PostSerializer)
    """
    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'count': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Total number of items"
            ),
            'next': openapi.Schema(
                type=openapi.TYPE_STRING,
                description="URL for the next page"
            ),
            'previous': openapi.Schema(
                type=openapi.TYPE_STRING,
                description="URL for the previous page"
            ),
            'results': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=get_serializer_schema(item_schema),
                description="List of items"
            ),
        }
    )

def get_standard_response_schema(data_schema=None):
    """
    Generate OpenAPI schema for standard API response format.

    Creates a schema for the standard response envelope containing code, message
    and data fields. Used to document consistent API responses.

    Args:
        data_schema: Schema for the data field payload. Can be a Serializer class
                    or a pagination schema from get_pagination_schema()

    Examples:
        # For paginated responses:
        @swagger_auto_schema(
            responses={200: get_standard_response_schema(
                get_pagination_schema(PostSerializer)
            )}
        )
        def get(self, request):
            ...

        # For regular responses:
        @swagger_auto_schema(
            responses={200: get_standard_response_schema(UserSerializer)}
        )
        def get(self, request):
            ...
    """
    data_field = (data_schema if isinstance(data_schema, openapi.Schema)
                 else get_serializer_schema(data_schema) if data_schema
                 else openapi.Schema(type=openapi.TYPE_OBJECT))

    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'code': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Response code, 0 means success"
            ),
            'message': openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Response message"
            ),
            'data': data_field
        }
    )

def get_openapi_field(field):
    """
    Convert DRF serializer field to OpenAPI Schema.

    Maps Django REST Framework serializer fields to their corresponding OpenAPI
    schema types. Supports common field types like Integer, String, etc.

    Args:
        field: DRF serializer field instance
    """
    if isinstance(field, IntegerField):
        return openapi.Schema(type=openapi.TYPE_INTEGER)
    elif isinstance(field, CharField):
        return openapi.Schema(type=openapi.TYPE_STRING)
    elif isinstance(field, FloatField):
        return openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT)
    elif isinstance(field, DateTimeField):
        return openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
    else:
        return openapi.Schema(type=openapi.TYPE_STRING)

def get_serializer_schema(serializer_class):
    """
    Convert DRF serializer to OpenAPI Schema.

    Automatically generates an OpenAPI schema from a serializer class by mapping
    all its fields to corresponding schema types.

    Args:
        serializer_class: DRF Serializer class to convert
    """
    properties = {}
    for field_name, field in serializer_class().get_fields().items():
        properties[field_name] = get_openapi_field(field)
    return openapi.Schema(type=openapi.TYPE_OBJECT, properties=properties)

def get_error_response_schema(code=None, message=None):
    """
    Get OpenAPI schema for error responses.

    Args:
        code: Optional error code to use
        message: Optional error message to use

    Returns:
        openapi.Schema: Schema for error responses
    """
    properties = {
        'code': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="Error code, non-zero indicates error",
            default=code if code is not None else 500
        ),
        'message': openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Error message",
            default=message if message is not None else "Internal server error"
        ),
        'data': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Detailed error message"
                )
            }
        )
    }

    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=properties
    )
