from random import choice

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.views import View

from .models import StorageServer, StoredFile
from .utils.request import get_query_params, require_auth, servers_to_dict_list, servers_to_json_response


@require_auth
def retrieve_storage_servers(request: WSGIRequest):
    return JsonResponse({"hosts": servers_to_dict_list(StorageServer.objects.get_active())})


@require_auth
def register_new_storage_server(request: WSGIRequest):
    param = get_query_params(request, ["space", "host", "port"], types=[int, str, str])

    if isinstance(param, HttpResponse):
        return param

    space, host, port = param
    if not StorageServer.objects.filter(host=host, port=port).exists():
        new_server = StorageServer.objects.create(host=host, port=port, available_space=space)
        return JsonResponse({"id": new_server.id}, status=201)

    return HttpResponse("Already exists", status=200)


@require_auth
def recover_server(request: WSGIRequest):
    param = get_query_params(request, ["space", "host", "port"], types=[int])
    if isinstance(param, HttpResponse):
        return param
    space, host, port = param

    try:
        server = StorageServer.objects.get(host=host, port=port)
    except StorageServer.DoesNotExist:
        return HttpResponse("Such server didn't register", status=404)

    server.update(status=server.StorageServerStatuses.RUNNING, available_space=space)

    return HttpResponse("Recover completed", status=200)


class FileView(View):
    def get(self, request: WSGIRequest):
        param = get_query_params(request, ["name", "cwd"])
        if isinstance(param, HttpResponse):
            return param

        file_name, cwd = param
        full_name = f"{cwd}/{file_name}"

        try:
            stored_file = StoredFile.objects.get(name=full_name)
            return servers_to_json_response(
                [
                    choice(list(stored_file.hosts.filter(status=StorageServer.StorageServerStatuses.RUNNING))),
                ],
                fields=["host", "port"],
            )

        except StoredFile.DoesNotExist:
            return HttpResponse("Such file doesn't exist", status=404)

    def post(self, request: WSGIRequest):
        param = get_query_params(request, ["name", "size", "cwd"])
        if isinstance(param, HttpResponse):
            return param

        file_name, size, cwd = param
        full_name = f"{cwd}/{file_name}"

        try:
            # NOTE: we use model as dataclass here. that's shit
            # TODO: create a UnsavedFileInfo dataclass
            new_file = StoredFile(name=full_name, size=size)
            return JsonResponse(
                {
                    "hosts": servers_to_dict_list(
                        [
                            StorageServer.objects.get_allocation(new_file),
                        ]
                    )
                },
                status=200,
            )

        except ValueError as e:
            return HttpResponse(str(e), status=507)
