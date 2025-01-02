from django.urls import path
"""
URL configuration for the sample app in the v1 API.

This module defines URL patterns for the sample app, including paths for
creating and listing posts, tags, and categories.

Routes:
- 'posts/': Provides a list of posts and allows for creating new posts.
- 'tags/': Provides a list of tags and allows for creating new tags.
- 'categories/': Provides a list of categories and allows for creating new
    categories.

Each route is associated with a corresponding view that handles the request.

Views:
- PostListCreateAPIView: Handles listing and creating posts.
- TagListCreateAPIView: Handles listing and creating tags.
- CategoryListCreateAPIView: Handles listing and creating categories.
"""
from .views import (
        PostListCreateAPIView,
        TagListCreateAPIView,
        CategoryListCreateAPIView,
)

urlpatterns = [
    path(
        'posts/',
        PostListCreateAPIView.as_view(),
        name='post-list-create'
    ),
    path(
        'tags/',
        TagListCreateAPIView.as_view(),
        name='tag-list-create'
    ),
    path(
        'categories/',
        CategoryListCreateAPIView.as_view(),
        name='category-list-create'
    ),
]