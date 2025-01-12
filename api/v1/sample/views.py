import logging
import time

from django_celery_beat.models import IntervalSchedule, PeriodicTask
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Post, Tag
from .serializers import (
    CategorySerializer,
    PostSerializer,
    PostUpdateSerializer,
    TagSerializer,
)
from .tasks import async_task


class PostListCreateView(APIView):
    """
    API endpoint for listing and creating posts.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a list of all posts",
        responses={200: PostSerializer(many=True)}
    )
    def get(self, request):
        """Returns a list of all posts"""
        try:
            posts = Post.objects.all()
            serializer = PostSerializer(posts, many=True)
            return Response(serializer.data)
        except Exception as e:
            logging.error(f"Error fetching posts: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Create a new post",
        request_body=PostSerializer,
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'post': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'task_id': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Celery task ID'
                    )
                }
            )
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

                # Trigger sample task
                task = async_task.delay(post.id)

                # Return both post data and task id
                return Response({
                    "post": serializer.data,
                    "task_id": task.id
                }, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Error creating post: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
            200: PostSerializer,
            404: "Not found"
        }
    )
    def get(self, request, pk):
        """Returns a specific post"""
        try:
            post = self.get_object(pk)
            if not post:
                return Response(
                    {"error": "Post not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = PostSerializer(post)
            return Response(serializer.data)
        except Exception as e:
            logging.error(f"Error retrieving post {pk}: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Update a specific post",
        request_body=PostUpdateSerializer,
        responses={
            200: PostUpdateSerializer,
            404: "Not found"
        }
    )
    def put(self, request, pk):
        """Updates a specific post"""
        try:
            post = self.get_object(pk)
            if not post:
                return Response(
                    {"error": "Post not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = PostUpdateSerializer(post, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Error updating post {pk}: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Delete a specific post",
        responses={
            204: "No Content",
            404: "Not found"
        }
    )
    def delete(self, request, pk):
        """Deletes a specific post"""
        try:
            post = self.get_object(pk)
            if not post:
                return Response(
                    {"error": "Post not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logging.error(f"Error deleting post {pk}: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Tag views
class TagListCreateView(APIView):
    """
    API endpoint for listing and creating tags.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a list of all tags",
        responses={200: TagSerializer(many=True)}
    )
    def get(self, request):
        """Returns a list of all tags"""
        try:
            tags = Tag.objects.all()
            serializer = TagSerializer(tags, many=True)
            return Response(serializer.data)
        except Exception as e:
            logging.error(f"Error fetching tags: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Create a new tag",
        request_body=TagSerializer,
        responses={201: TagSerializer}
    )
    def post(self, request):
        """Creates a new tag"""
        try:
            serializer = TagSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Error creating tag: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
            200: TagSerializer,
            404: "Not found"
        }
    )
    def get(self, request, pk):
        """Returns a specific tag"""
        try:
            tag = self.get_object(pk)
            if not tag:
                return Response(
                    {"error": "Tag not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = TagSerializer(tag)
            return Response(serializer.data)
        except Exception as e:
            logging.error(f"Error retrieving tag {pk}: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Update a specific tag",
        request_body=TagSerializer,
        responses={
            200: TagSerializer,
            404: "Not found"
        }
    )
    def put(self, request, pk):
        """Updates a specific tag"""
        try:
            tag = self.get_object(pk)
            if not tag:
                return Response(
                    {"error": "Tag not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = TagSerializer(tag, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Error updating tag {pk}: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Delete a specific tag",
        responses={
            204: "No Content",
            404: "Not found"
        }
    )
    def delete(self, request, pk):
        """Deletes a specific tag"""
        try:
            tag = self.get_object(pk)
            if not tag:
                return Response(
                    {"error": "Tag not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            tag.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logging.error(f"Error deleting tag {pk}: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Category views
class CategoryListCreateView(APIView):
    """
    API endpoint for listing and creating categories.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a list of all categories",
        responses={200: CategorySerializer(many=True)}
    )
    def get(self, request):
        """Returns a list of all categories"""
        try:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data)
        except Exception as e:
            logging.error(f"Error fetching categories: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Create a new category",
        request_body=CategorySerializer,
        responses={201: CategorySerializer}
    )
    def post(self, request):
        """Creates a new category"""
        try:
            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Error creating category: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
            200: CategorySerializer,
            404: "Not found"
        }
    )
    def get(self, request, pk):
        """Returns a specific category"""
        try:
            category = self.get_object(pk)
            if not category:
                return Response(
                    {"error": "Category not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Exception as e:
            logging.error(f"Error retrieving category {pk}: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Update a specific category",
        request_body=CategorySerializer,
        responses={
            200: CategorySerializer,
            404: "Not found"
        }
    )
    def put(self, request, pk):
        """Updates a specific category"""
        try:
            category = self.get_object(pk)
            if not category:
                return Response(
                    {"error": "Category not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = CategorySerializer(category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(f"Error updating category {pk}: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Delete a specific category",
        responses={
            204: "No Content",
            404: "Not found"
        }
    )
    def delete(self, request, pk):
        """Deletes a specific category"""
        try:
            category = self.get_object(pk)
            if not category:
                return Response(
                    {"error": "Category not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logging.error(f"Error deleting category {pk}: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )