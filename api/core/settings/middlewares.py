import json
import logging

from django.http import JsonResponse
from django.urls import reverse
from rest_framework.response import Response

# Set up logging
logger = logging.getLogger(__name__)

class AxiosResponseMiddleware:
    """
    Middleware to convert Django's JsonResponse into a format 
    compatible with AxiosResponse.
    """

    def __init__(self, get_response):
        """
        Initializes the middleware with the next middleware or view.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Processes the request and response through the middleware.
        """
        if request.path.startswith(reverse('schema-swagger-ui')):
            return self.get_response(request)

        logger.debug(f"Request: {request.method} {request.path}")
        response = self.get_response(request)

        if isinstance(response, Response):
            data = response.data

            axios_response = {
                'data': data,
                'code': 0
            }
            logger.debug(f"AxiosResponse: {axios_response}")

            return JsonResponse(axios_response, status=response.status_code)
        
        return response