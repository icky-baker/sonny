from django.core.handlers.wsgi import WSGIRequest
from django.forms import model_to_dict
from django.http import Http404, HttpResponse, JsonResponse

from .models import StorageServer, StoredFile
from .utils.request import extract_socket, get_query_params


# TODO: add available space from query params here
def register_new_storage_server(request: WSGIRequest):
    host, port = extract_socket(request)
    param = get_query_params(request, ["space"], types=[int])
    if isinstance(param, HttpResponse):
        return param

    space = param[0]
    if not StorageServer.objects.filter(host=host, port=port).exists():
        # FIXME: hardcode value here
        new_server = StorageServer.objects.create(host=host, port=port, available_space=space)
        return JsonResponse({"id": new_server.id}, status=201)

    return HttpResponse("Already exists", status=200)


def recover_server(request: WSGIRequest):
    host, port = extract_socket(request)

    param = get_query_params(request, ["space"], types=[int])
    if isinstance(param, HttpResponse):
        return param
    space = param[0]

    try:
        server = StorageServer.objects.get(host=host, port=port)
    except StorageServer.DoesNotExist:
        return HttpResponse("Such server didn't register", status=404)

    server.update(status=server.StorageServerStatuses.RUNNING, available_space=space)

    return HttpResponse("Recover completed", status=200)


def allocate_file(request: WSGIRequest):
    """
    Let body be
    {
        "size": X in bytes
    }
    """
    param = get_query_params(request, ["name", "size"])
    if isinstance(param, HttpResponse):
        return param

    filename, size = param

    try:
        servers = StorageServer.objects.allocate(StoredFile.objects.create(name=filename, size=size))
        return JsonResponse(
            list(map(lambda m: model_to_dict(m, ["host", "port", "available_space"]), servers)),
            status=200,
            safe=False,
        )
    except ValueError as e:
        return HttpResponse(str(e), status=507)
