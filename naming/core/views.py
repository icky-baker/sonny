from random import choice

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.views import View

from .models import StorageServer, StoredFile
from .utils.request import (
    extract_socket,
    get_query_params,
    require_auth,
    servers_to_dict_list,
    servers_to_json_response,
)


@require_auth
def retrieve_storage_servers(request: WSGIRequest):
    return JsonResponse({"hosts": servers_to_dict_list(StorageServer.objects.get_active(), fields=["host", "port"])})


@require_auth
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


@require_auth
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


class FileView(View):
    def get(self, request: WSGIRequest):
        param = get_query_params(request, ["name"])
        if isinstance(param, HttpResponse):
            return param

        filename = param

        try:
            stored_file = StoredFile.objects.get(name=filename)
            return servers_to_json_response(
                [
                    choice(list(stored_file.hosts.filter(status=StorageServer.StorageServerStatuses.RUNNING))),
                ],
                fields=["host", "port"],
            )

        except StoredFile.DoesNotExist:
            return HttpResponse("Such file doesn't exist", status=404)

    def post(self, request: WSGIRequest):
        param = get_query_params(request, ["name", "size"])
        if isinstance(param, HttpResponse):
            return param

        filename, size = param
        try:
            new_file = StoredFile.objects.create(name=filename, size=size)
            servers = StorageServer.objects.allocate(new_file)
            return JsonResponse({"hosts": servers_to_dict_list(servers)}, status=200)

        except ValueError as e:
            return HttpResponse(str(e), status=507)
