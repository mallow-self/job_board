import datetime
import logging
from typing import Callable
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    Middleware that logs the HTTP method, path, and processing time of each request.

    Logs the start time when a request is received and logs the end time along with
    the total duration taken to process the request.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start_time = datetime.datetime.now()
        logger.info(f"[{start_time}] {request.method} {request.path}")
        response = self.get_response(request)
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(
            f"[{end_time}] {request.method} {request.path} completed in {duration} sec"
        )
        return response
