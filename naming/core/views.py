from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404, HttpResponse, JsonResponse

from .models import StorageServer
from .utils.socket import extract_socket


def register_new_storage_server(request: WSGIRequest):
    host, port = extract_socket(request)
    if not StorageServer.objects.filter(host=host, port=port).exists():
        new_server = StorageServer.objects.create(host=host, port=port)
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
