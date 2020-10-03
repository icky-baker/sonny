import json
from random import choice

from core.models import StorageServer, StoredFile
from core.utils.files import get_full_name
from core.utils.request import (
    file_list_to_dict_list,
    get_query_params,
    require_auth,
    servers_to_dict_list,
    servers_to_json_response,
)
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.views import View


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

    server = StorageServer.objects.get(host=host, port=port)
    server.update(status=server.StorageServerStatuses.RUNNING, available_space=space)
    return HttpResponse("Status updated", status=200)


class FileView(View):
    def get(self, request: WSGIRequest):
        param = get_query_params(request, ["name", "cwd"])
        if isinstance(param, HttpResponse):
            return param

        file_name, cwd = param
        full_name = get_full_name(cwd, file_name)

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
        full_name = get_full_name(cwd, file_name)

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


def file_approve(request: WSGIRequest):
    param = get_query_params(request, ["name", "host", "port", "cwd"])

    if isinstance(param, HttpResponse):
        return param

    file_name, host, port, cwd = param
    full_name = get_full_name(cwd, file_name)

    file_meta_info = json.loads(request.body)
    new_file = StoredFile.objects.create(name=full_name, size=file_meta_info["size"], meta=file_meta_info)
    sender_host = StorageServer.objects.get(host=host, port=port)
    new_file.hosts.add(sender_host)
    new_file.save()

    return HttpResponse(status=200)


def file_delete(request: WSGIRequest):
    param = get_query_params(request, ["name", "host", "port", "cwd"])

    if isinstance(param, HttpResponse):
        return param

    file_name, host, port, cwd = param
    full_name = get_full_name(cwd, file_name)

    try:
        file = StoredFile.objects.get(name=full_name)
    except StoredFile.DoesNotExist:
        return HttpResponse(status=400)

    file.detele()
    return HttpResponse(status=200)


def retrieve_directory_content(request: WSGIRequest):
    param = get_query_params(request, ["name"])
    if isinstance(param, HttpResponse):
        return param
    dir_name = param[0]

    if not StoredFile.objects.filter(name=dir_name).exists():
        return HttpResponse("Directory doesn't exist", status=400)

    file = StoredFile.objects.get(name=dir_name)
    sub_files = file.get_sub_files()
    return JsonResponse({"files": file_list_to_dict_list(sub_files)}, status=200)
