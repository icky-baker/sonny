from typing import List, Tuple, Union

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse


def extract_socket(request: WSGIRequest) -> Tuple[str, str]:
    return request.get_host().split(":")


def get_query_params(request: WSGIRequest, names: List[str], types: list = None) -> Union[list, HttpResponse]:
    types = types or []
    param_values = [request.GET.get(name, None) for name in names]

    if [val for val in param_values if val is None]:
        missed_params = [name for name, value in zip(names, param_values) if value is None]

        return HttpResponse(f"Provide {','.join(missed_params)} in query params", status=400)

    if types:
        return [cast(value) for cast, value in zip(types, param_values)]

    return param_values
