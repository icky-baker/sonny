from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

from .commands import (
    dir_delete,
    dir_make,
    dir_read,
    file_copy,
    file_create,
    file_delete,
    file_info,
    file_move,
    file_read,
    file_write,
    init,
)


def index(request):
    return HttpResponse(status=200)


def dfs(request):
    command = request.GET.get("command", None)
    name = request.GET.get("name", None)
    path = request.GET.get("path", None)
    cwd = request.GET.get("cwd", "/")

    if command == "init":
        response = init()
    elif command == "file_create":
        response = file_create(name=name, cwd=cwd)
    elif command == "file_read":
        response = file_read(name=name, cwd=cwd)
    elif command == "file_write":
        response = file_write(request=request, cwd=cwd)
    elif command == "file_delete":
        response = file_delete(name=name, cwd=cwd)
    elif command == "file_info":
        response = file_info(name=name, cwd=cwd)
    elif command == "file_copy":
        response = file_copy(name=name, cwd=cwd)
    elif command == "file_move":
        response = file_move(name=name, cwd=cwd, path=path)
    elif command == "dir_read":
        response = dir_read(cwd=cwd)
    elif command == "dir_make":
        response = dir_make(name=name, cwd=cwd)
    elif command == "dir_delete":
        response = dir_delete(cwd=cwd)
    else:
        response = HttpResponse(status=400)

    return response
