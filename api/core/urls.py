from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include

from .swagger import schema_view
from accounts.views import WeChatAppLoginView

# Define project URL routing configuration
urlpatterns = [
    # Health check endpoint
    # Used by Docker/Kubernetes for container health monitoring
    # Returns a simple 'OK' response to indicate the application is running
    path('health', lambda _: JsonResponse({'health': 'OK'}, status=200)),
    

    # Swagger UI documentation route
    # Displays the API documentation using Swagger UI.
    # The 'cache_timeout=0' ensures the documentation is regenerated on each
    # access.
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui',
    ),

    # Django admin site route
    # Provides access to the Django Admin interface for managing models and
    # data.
    path('admin/', admin.site.urls),

    # Authentication routes
    # Includes authentication endpoints provided by dj-rest-auth.
    path('api/v1/auth/', include('dj_rest_auth.urls')),

    # API routes for the cloud_platform application
    # Includes the URLs for APIs under the 'v1/sample' app.
    # path('api/v1/', include('v1.sample.urls')),

    # FIXME(Ray): Implement this method according to real project
    # Simulates WeChat mini-program login functionality
    # Endpoint for WeChat authentication
    path('api/v1/auth/wechat/login/',
         WeChatAppLoginView.as_view(),
         name='wechat_auth'),

    path('api/v1/', include('v1.sample.urls')),
]
