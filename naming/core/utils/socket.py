from typing import Tuple

from django.core.handlers.wsgi import WSGIRequest


def extract_socket(request: WSGIRequest) -> Tuple[str, str]:
    return request.get_host().split(":")
