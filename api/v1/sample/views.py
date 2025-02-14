import logging
import time

from django_celery_beat.models import IntervalSchedule, PeriodicTask
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.paginations import APIPagination
from core.swagger import (get_pagination_schema,
                          get_standard_response_schema,
                          get_page_parameters,
                          get_error_response_schema,
                          get_list_response_schema)
from .models import Category, Post, Tag
from .serializers import (
    CategorySerializer,
    PostSerializer,
    PostUpdateSerializer,
    TagSerializer,
)
from .tasks import async_task
from utils.constrants import SUCCESS_CODE


class PostListCreateView(APIView):
    """
    API endpoint for listing and creating posts.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a list of all posts with pagination",
        manual_parameters=get_page_parameters(),
        responses={
            200: get_standard_response_schema(
                get_pagination_schema(PostSerializer)
            ),
            500: get_error_response_schema(code=500)
        }
    )
    def get(self, request):
        """
        Returns a list of all posts.
        """
        try:
            # Pagination Notes:
            #
            # APIView requires manual pagination handling in get() method.
            #
            # GenericAPIView provides automatic pagination by setting the
            # pagination_class attribute.
            #
            # Example:
            #   class PostListCreateView(GenericAPIView):
            #       pagination_class = APIPagination
            #
            posts = Post.objects.all()
            paginator = APIPagination()
            paginated_posts = paginator.paginate_queryset(posts, request)
            serializer = PostSerializer(paginated_posts, many=True)

            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            logging.error(f"Error fetching posts: {str(e)}")
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "data": {"error": "Internal server error"}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new post",
        request_body=PostSerializer,
        responses={
            201: get_standard_response_schema(PostSerializer)
        }
    )
    def post(self, request):
        """Creates a new post and triggers sample task"""
        try:
            serializer = PostSerializer(
                data=request.data,
                context={"user": request.user}
            )
            if serializer.is_valid():
                # Save the post
                post = serializer.save()

                # Return both post data and task id
                return Response({
                    "code": SUCCESS_CODE,
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Error creating post: {str(e)}")
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "data": {"error": "Internal server error"}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PostDetailView(APIView):
    """
    API endpoint for retrieving, updating and deleting posts.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return None
        except Exception as e:
            logging.error(f"Error fetching post {pk}: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_description="Get a specific post",
        responses={
            200: get_standard_response_schema(PostSerializer),
            404: get_error_response_schema(code=404)
        }
    )
    def get(self, request, pk):
        """Returns a specific post"""
        try:
            post = self.get_object(pk)
            if not post:
                return Response({
                    "code": status.HTTP_404_NOT_FOUND,
                    "data": {"error": "Post not found"}
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = PostSerializer(post)
            return Response({
                "code": SUCCESS_CODE,
                "data": serializer.data
            })
        except Exception as e:
            logging.error(f"Error retrieving post {pk}: {str(e)}")
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "data": {"error": "Internal server error"}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update a specific post",
        request_body=PostUpdateSerializer,
        responses={
            200: get_standard_response_schema(PostUpdateSerializer),
            404: get_error_response_schema(code=404)
        }
    )
    def put(self, request, pk):
        """Updates a specific post"""
        try:
            post = self.get_object(pk)
            if not post:
                return Response({
                    "code": status.HTTP_404_NOT_FOUND,
                    "data": {"error": "Post not found"}
                }, status=status.HTTP_404_NOT_FOUND)
            serializer = PostUpdateSerializer(post, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "code": SUCCESS_CODE,
                    "data": serializer.data
                })
            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Error updating post {pk}: {str(e)}")
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "data": {"error": "Internal server error"}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Delete a specific post",
        responses={
            204: get_standard_response_schema(),
            404: get_error_response_schema(code=404)
        }
    )
    def delete(self, request, pk):
        """Deletes a specific post"""
        try:
            post = self.get_object(pk)
            if not post:
                return Response({
                    "code": status.HTTP_404_NOT_FOUND,
                    "data": {"error": "Post not found"}
                }, status=status.HTTP_404_NOT_FOUND)
            post.delete()
            return Response({
                "code": SUCCESS_CODE,
                "data": {}
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logging.error(f"Error deleting post {pk}: {str(e)}")
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "data": {"error": "Internal server error"}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Tag views
class TagListCreateView(APIView):
    """
    API endpoint for listing and creating tags.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a list of all tags",
        responses={
            200: get_standard_response_schema(
                get_list_response_schema(TagSerializer)
            )
        }
    )
    def get(self, request):
        """Returns a list of all tags"""
        try:
            tags = Tag.objects.all()
            serializer = TagSerializer(tags, many=True)
            return Response({
                "code": SUCCESS_CODE,
                "data": serializer.data
            })
        except Exception as e:
            logging.error(f"Error fetching tags: {str(e)}")
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "data": {"error": "Internal server error"}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new tag",
        request_body=TagSerializer,
        responses={
            201: get_standard_response_schema(TagSerializer)
        }
    )
    def post(self, request):
        """Creates a new tag"""
        try:
            serializer = TagSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "code": SUCCESS_CODE,
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Error creating tag: {str(e)}")
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "data": {"error": "Internal server error"}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TagDetailView(APIView):
    """
    API endpoint for retrieving, updating and deleting tags.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Tag.objects.get(pk=pk)
        except Tag.DoesNotExist:
            return None
        except Exception as e:
            logging.error(f"Error fetching tag {pk}: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_description="Get a specific tag",
        responses={
            200: get_standard_response_schema(TagSerializer),
            404: get_error_response_schema(code=404)
        }
    )
    def get(self, request, pk):
        """Returns a specific tag"""
        try:
            tag = self.get_object(pk)
            if not tag:
                return Response({
                    "code": status.HTTP_404_NOT_FOUND,
                    "data": {"error": "Tag not found"}
                }, status=status.HTTP_404_NOT_FOUND)
            serializer = TagSerializer(tag)
            return Response({
                "code": SUCCESS_CODE,
                "data": serializer.data
            })
        except Exception as e:
            logging.error(f"Error retrieving tag {pk}: {str(e)}")
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "data": {"error": "Internal server error"}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update a specific tag",
        request_body=TagSerializer,
        responses={
            200: get_standard_response_schema(TagSerializer),
            404: get_error_response_schema(code=404)
        }
    )
    def put(self, request, pk):
        """Updates a specific tag"""
        try:
            tag = self.get_object(pk)
            if not tag:
                return Response({
                    "code": status.HTTP_404_NOT_FOUND,
                    "data": {"error": "Tag not found"}
                }, status=status.HTTP_404_NOT_FOUND)
            serializer = TagSerializer(tag, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "code": SUCCESS_CODE,
                    "data": serializer.data
                })
            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Error updating tag {pk}: {str(e)}")
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "data": {"error": "Internal server error"}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Delete a specific tag",
        responses={
            204: get_standard_response_schema({}),
            404: get_error_response_schema(code=404)
        }
    )
    def delete(self, request, pk):
        """Deletes a specific tag"""
        try:
            tag = self.get_object(pk)
            if not tag:
                return Response({
                    "code": status.HTTP_404_NOT_FOUND,
                    "data": {"error": "Tag not found"}
                }, status=status.HTTP_404_NOT_FOUND)
            tag.delete()
            return Response({
                "code": SUCCESS_CODE,
                "data": {}
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logging.error(f"Error deleting tag {pk}: {str(e)}")
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "data": {"error": "Internal server error"}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Category views
class CategoryListCreateView(APIView):
    """
    API endpoint for listing and creating categories.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a list of all categories",
        responses={
            200: get_standard_response_schema(
                get_list_response_schema(CategorySerializer)
            )
        }
    )
    def get(self, request):
        """Returns a list of all categories"""
        try:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return Response({
                "code": SUCCESS_CODE,
                "data": serializer.data
            })
        except Exception as e:
            logging.error(f"Error fetching categories: {str(e)}")
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "data": {"error": "Internal server error"}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new category",
        request_body=CategorySerializer,
        responses={
            201: get_standard_response_schema(CategorySerializer)
        }
    )
    def post(self, request):
        """Creates a new category"""
        try:
            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "code": SUCCESS_CODE,
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Error creating category: {str(e)}")
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "data": {"error": "Internal server error"}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryDetailView(APIView):
    """
    API endpoint for retrieving, updating and deleting categories.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None
        except Exception as e:
            logging.error(f"Error fetching category {pk}: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_description="Get a specific category",
        responses={
            200: get_standard_response_schema(CategorySerializer),
            404: get_error_response_schema(code=404)
        }
    )
    def get(self, request, pk):
        """Returns a specific category"""
        try:
            category = self.get_object(pk)
            if not category:
                return Response({
                    "code": status.HTTP_404_NOT_FOUND,
                    "data": {"error": "Category not found"}
                }, status=status.HTTP_404_NOT_FOUND)
            serializer = CategorySerializer(category)
            return Response({
                "code": SUCCESS_CODE,
                "data": serializer.data
            })
        except Exception as e:
            logging.error(f"Error retrieving category {pk}: {str(e)}")
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "data": {"error": "Internal server error"}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update a specific category",
        request_body=CategorySerializer,
        responses={
            200: get_standard_response_schema(CategorySerializer),
            404: get_error_response_schema(code=404)
        }
    )
    def put(self, request, pk):
        """Updates a specific category"""
        try:
            category = self.get_object(pk)
            if not category:
                return Response({
                    "code": status.HTTP_404_NOT_FOUND,
                    "data": {"error": "Category not found"}
                }, status=status.HTTP_404_NOT_FOUND)
            serializer = CategorySerializer(category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "code": SUCCESS_CODE,
                    "data": serializer.data
                })
            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Error updating category {pk}: {str(e)}")
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "data": {"error": "Internal server error"}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Delete a specific category",
        responses={
            204: get_standard_response_schema({}),
            404: get_error_response_schema(code=404)
        }
    )
    def delete(self, request, pk):
        """Deletes a specific category"""
        try:
            category = self.get_object(pk)
            if not category:
                return Response({
                    "code": status.HTTP_404_NOT_FOUND,
                    "data": {"error": "Category not found"}
                }, status=status.HTTP_404_NOT_FOUND)
            category.delete()
            return Response({
                "code": SUCCESS_CODE,
                "data": {}
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logging.error(f"Error deleting category {pk}: {str(e)}")
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "data": {"error": "Internal server error"}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)