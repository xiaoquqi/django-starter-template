from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema

from .models import Post, Tag, Category
from .serializers import PostSerializer, TagSerializer, CategorySerializer
from .tasks import async_task

class PostListCreateAPIView(APIView):
    """
    API view to retrieve a list of posts or create a new post.

    Methods
    -------
    get(request):
        Retrieves a list of all posts.
        - Returns:
            Response: A response object containing serialized post data.

    post(request):
        Creates a new post with associated tags and categories.
        - Parameters:
            request (Request): The request object containing post data.
        - Returns:
            Response: A response object containing serialized post data if
                      successful, or error details if the request is invalid.
    """

    @swagger_auto_schema(responses={200: PostSerializer(many=True)})
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=PostSerializer, responses={201: PostSerializer}
    )
    def post(self, request):
        # Use PostSerializer for data validation and creation
        user = request.user if request else None
        serializer = PostSerializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            # Call the overridden `create` method
            post = serializer.save()

            # NOTE(Ray): This is where the asynchronous task is called
            async_task.delay(post.id)

            return Response(PostSerializer(post).data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagListCreateAPIView(APIView):

    @swagger_auto_schema(responses={200: TagSerializer(many=True)})
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=TagSerializer, responses={201: TagSerializer}
    )
    def post(self, request):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryListCreateAPIView(APIView):

    @swagger_auto_schema(responses={200: CategorySerializer(many=True)})
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=CategorySerializer, responses={201: CategorySerializer}
    )
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)