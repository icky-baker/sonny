import functools
from typing import Any, Dict, Iterable, List, Optional, Union

from core.models import StorageServer, StoredFile
from django.core.handlers.wsgi import WSGIRequest
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse


def get_query_params(request: WSGIRequest, names: List[str], types: list = None) -> Union[list, HttpResponse]:
    types = types or []
    param_values = [request.GET.get(name, None) for name in names]
    if not param_values:
        param_values = [request.POST.get(name, None) for name in names]

    if [val for val in param_values if val is None]:
        missed_params = [name for name, value in zip(names, param_values) if value is None]

        return HttpResponse(f"Provide {', '.join(missed_params)} in query params", status=400)

    if types:
        return [cast(value) for cast, value in zip(types, param_values)]

    return param_values


def require_auth(f):
    @functools.wraps(f)
    def wrapper(request: WSGIRequest, *args, **kwargs):
        from naming import settings

        hash = request.headers.get("Server-Hash")

        auth_passed = (
            not hasattr(settings, "STORAGE_SERVER_SECRET_HASH") or hash == settings.STORAGE_SERVER_SECRET_HASH
        )

        if not auth_passed:
            return HttpResponse("Go away", status=401)
        return f(request, *args, **kwargs)

    return wrapper


def servers_to_dict_list(
    servers: Iterable[StorageServer], fields: List[str] = None
) -> List[Dict[str, Any,]]:
    fields = fields or ["host", "port", "available_space"]
    return list(map(lambda m: model_to_dict(m, fields), servers))


def servers_to_json_response(
    servers: Iterable[StorageServer], fields: List[str] = None, file: Optional[StoredFile] = None
) -> HttpResponse:
    res = {"hosts": servers_to_dict_list(servers, fields)}
    if file:
        res["file_info"] = file.meta

    return JsonResponse(
        res,
        status=200,
        safe=False,
    )


def file_list_to_dict_list(files: Iterable[StoredFile]) -> List[Dict[str, Any]]:
    # fields = fields or ["name", "size", "meta"]

    return list(map(lambda m: m.to_dict(), files))
