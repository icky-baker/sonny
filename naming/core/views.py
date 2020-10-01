import json

from django.core.handlers.wsgi import WSGIRequest
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse

from .models import StorageServer, StoredFile
from .utils.socket import extract_socket


# TODO: add available space from query params here
def register_new_storage_server(request: WSGIRequest):
    host, port = extract_socket(request)
    if not StorageServer.objects.filter(host=host, port=port).exists():
        # FIXME: hardcode value here
        new_server = StorageServer.objects.create(host=host, port=port, available_space=12320)
        return JsonResponse({"id": new_server.id}, status=201)

    return HttpResponse("Already exists", status=200)


def recover_server(request: WSGIRequest):
    host, port = extract_socket(request)

    try:
        server = StorageServer.objects.get(host=host, port=port)
    except StorageServer.DoesNotExist:
        return HttpResponse("Such server didn't register", status=404)

    server.update(status=server.StorageServerStates.RUNNING)

    return HttpResponse(status=200)


def allocate_file(request: WSGIRequest):
    """
    Let body be
    {
        "size": X in bytes
    }
    """
    filename, size = request.GET.get("filename"), request.GET.get("size")
    if not filename or not size:
        return HttpResponse("Provide filename and size in query params")

    try:
        servers = StorageServer.objects.allocate(StoredFile.objects.create(name=filename, size=size))
        return JsonResponse(
            list(map(lambda m: model_to_dict(m, ["host", "port", "available_space"]), servers)),
            status=200,
            safe=False,
        )
    except ValueError as e:
        return HttpResponse(str(e), status=507)
