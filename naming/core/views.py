import json
import logging
from pathlib import Path
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
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.views import View

logger = logging.getLogger("common")


def init(request: WSGIRequest):
    StoredFile.objects.exclude(name="/").delete()
    StorageServer.objects.filter(status=StorageServer.StorageServerStatuses.DOWN).delete()
    return HttpResponse(status=200)


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
        server = StorageServer.objects.create(host=host, port=port, available_space=space)
        root_dir = StoredFile.objects.get(name="/")
        root_dir.hosts.add(server)
        root_dir.save()
        logger.info("New storage server: %s", server)

    else:

        server = StorageServer.objects.get(host=host, port=port)
        server.update(status=server.StorageServerStatuses.DOWN, available_space=space)

    return JsonResponse({"id": server.id, "files": file_list_to_dict_list(StoredFile.objects.all())}, status=200)


@require_auth
def approve_storage_server(request: WSGIRequest):
    param = get_query_params(request, ["space", "host", "port"], types=[int, str, str])

    if isinstance(param, HttpResponse):
        return param

    space, host, port = param
    if not StorageServer.objects.filter(host=host, port=port).exists():
        return HttpResponse(status=400)
    else:
        server = StorageServer.objects.get(host=host, port=port)
        server.update(status=server.StorageServerStatuses.RUNNING, available_space=space)

    return JsonResponse({"id": server.id}, status=200)


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
                file=stored_file,
            )

        except StoredFile.DoesNotExist:
            return HttpResponse({"hosts": []}, status=404)

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

    file_meta_info = request.POST
    if StoredFile.objects.filter(name=full_name).exists():
        new_file = StoredFile.objects.get(name=full_name)
    else:
        new_file = StoredFile.objects.create(
            name=full_name, size=file_meta_info.get("size", None), meta=file_meta_info
        )

    sender_host = StorageServer.objects.get(host=host, port=port)
    new_file.hosts.add(sender_host)
    new_file.save()

    hosts_without_file = StorageServer.objects.get_active().exclude(files=new_file)
    if new_file.size:
        hosts_without_file = hosts_without_file.filter(available_space__gt=new_file.size)

    if hosts_without_file.exists():
        return JsonResponse({"replicate_to": model_to_dict(hosts_without_file.first(), ["host", "port"])}, status=200)

    return JsonResponse({"replicate_to": None}, status=200)


def file_delete(request: WSGIRequest):
    param = get_query_params(request, ["name", "host", "port", "cwd"])

    if isinstance(param, HttpResponse):
        return param

    file_name, host, port, cwd = param
    logger.info(f"{cwd=}, {file_name=}")
    full_name = get_full_name(cwd, file_name)

    logger.info("full_name = %s", full_name)

    try:
        file = StoredFile.objects.get(name=full_name)
    except StoredFile.DoesNotExist:
        return HttpResponse(status=400)

    file.hosts.remove(StorageServer.objects.get(host=host, port=port))

    if not list(file.hosts.all()):
        file.delete()
        return JsonResponse({"replicate_to": None}, status=200)

    file.save()
    if file.hosts.exists():
        return JsonResponse({"replicate_to": model_to_dict(file.hosts.first(), ["host", "port"])}, status=200)
    else:
        return JsonResponse({"replicate_to": None}, status=200)


def retrieve_directory_content(request: WSGIRequest):
    param = get_query_params(request, ["name", "cwd"])
    if isinstance(param, HttpResponse):
        return param
    dir_name, cwd = param
    logger.info(f"dir name is {dir_name}")
    full_name_by_dir_name = {
        "..": str(Path(cwd).parent),
        ".": cwd[:-1],  # NOTE: because there is no slash at the end in DB, but there is a slash in input
    }
    full_name = full_name_by_dir_name.get(dir_name, get_full_name(cwd, dir_name))

    logger.info(f"full name is {full_name}")
    if not StoredFile.objects.filter(name=full_name).exists():
        return HttpResponse("Directory doesn't exist", status=400)

    file = StoredFile.objects.get(name=full_name)
    sub_files = file.get_sub_files()
    return JsonResponse({"files": file_list_to_dict_list(sub_files)}, status=200)
