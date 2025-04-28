import datetime
import logging

logger = logging.getLogger(__name__) 


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = datetime.datetime.now()
        logger.info(f"[{start_time}] {request.method} {request.path}")
        response = self.get_response(request)
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(
            f"[{end_time}] {request.method} {request.path} completed in {duration} sec"
        )
        return response
