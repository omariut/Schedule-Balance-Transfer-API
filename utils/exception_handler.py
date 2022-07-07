from rest_framework.views import Response, exception_handler
from rest_framework import status
from django.db import utils
from django.core.exceptions import ValidationError, BadRequest, ObjectDoesNotExist


def custom_exception_handler(exc, context):

    # Call REST framework's default exception handler first to get the standard error response.
    response = exception_handler(exc, context)

    # if there is an IntegrityError and the error response hasn't already been generated
    if isinstance(exc, Exception) and not response:
        response = Response(
            {"message": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    elif isinstance(exc, KeyError) and not response:

        response = Response(
            {"message": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    if isinstance(exc, BadRequest):
        message = exc.args[0]["message"]
        data = exc.args[0]["data"]
        return Response(
            {"message": message, "data": data}, status=status.HTTP_400_BAD_REQUEST
        )

    return response
