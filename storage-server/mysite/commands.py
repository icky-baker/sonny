import datetime
import os
import shutil
import time

from django.conf import settings
from django.http import FileResponse, HttpResponse, JsonResponse


def init():
    _, _, free = shutil.disk_usage("/")
    shutil.rmtree(settings.WORK_DIR)
    os.mkdir(settings.WORK_DIR)
    return JsonResponse({"msg": {"available_size": free // (2 ** 30)}}, status=200)


def file_create(name, cwd):
    if os.path.isfile(f"{settings.WORK_DIR}{cwd}{name}"):
        return JsonResponse({"msg": {"error": "file with such name already exists"}}, status=400)
    else:
        open(f"{settings.WORK_DIR}{cwd}{name}", "w+")
        return HttpResponse(status=201)


def file_read(name, cwd):
    if not os.path.isfile(f"{settings.WORK_DIR}{cwd}{name}"):
        return JsonResponse({"msg": {"error": "file with such name does not exists"}}, status=404)
    else:
        return FileResponse(open(f"{settings.WORK_DIR}{cwd}{name}", "rb"), as_attachment=True)


def handle_uploaded_file(file, cwd):
    with open(f"{settings.WORK_DIR}{cwd}{file.name}", "wb+") as dest:
        for chunk in file.chunks():
            dest.write(chunk)


def file_write(request, cwd):
    file = request.FILES["file"]
    # print(file.name)
    # print(file.size)
    # print(file.content_type)
    # print(file.content_type_extra)
    handle_uploaded_file(file=file, cwd=cwd)
    return HttpResponse(status=200)


def file_delete(name, cwd):
    if not os.path.isfile(f"{settings.WORK_DIR}{cwd}{name}"):
        return JsonResponse({"msg": {"error": "file with such name does not exists"}}, status=404)
    else:
        os.remove(f"{settings.WORK_DIR}{cwd}{name}")
        return HttpResponse(status=200)


def file_info(name, cwd):
    if not os.path.isfile(f"{settings.WORK_DIR}{cwd}{name}"):
        return JsonResponse({"msg": {"error": "file with such name does not exists"}}, status=404)
    else:
        return JsonResponse(
            {
                "msg": {
                    "File": name,
                    "Access time": time.ctime(os.path.getatime(f"{settings.WORK_DIR}{cwd}{name}")),
                    "Modified time": time.ctime(os.path.getmtime(f"{settings.WORK_DIR}{cwd}{name}")),
                    "Change time": time.ctime(os.path.getctime(f"{settings.WORK_DIR}{cwd}{name}")),
                    "Size": os.path.getsize(f"{settings.WORK_DIR}{cwd}{name}"),
                }
            },
            status=200,
        )


def file_copy(name, cwd):
    if not os.path.isfile(f"{settings.WORK_DIR}{cwd}{name}"):
        return JsonResponse({"msg": {"error": "file with such name does not exists"}}, status=404)
    else:
        now = str(datetime.datetime.now())[:19].replace(":", "_").replace("-", "_")
        spltd_name = name.split(".")
        target = f"{spltd_name[0]}_{now}.{'.'.join(spltd_name[1::])}"
        shutil.copyfile(f"{settings.WORK_DIR}{cwd}{name}", f"{settings.WORK_DIR}{cwd}{target}")
        return JsonResponse({"msg": {"filename": target}}, status=404)


def file_move(name, cwd, path):
    if not os.path.isfile(f"{settings.WORK_DIR}{cwd}{name}"):
        return JsonResponse({"msg": {"error": "file with such name does not exists"}}, status=404)
    else:
        shutil.move(f"{settings.WORK_DIR}{cwd}{name}", f"{settings.WORK_DIR}{path}{name}")
        return HttpResponse(status=200)


def dir_read(cwd):
    if not os.path.isdir(f"{settings.WORK_DIR}{cwd}"):
        return JsonResponse({"msg": {"error": "directory with such name does not exists"}}, status=404)
    else:
        files = [
            f
            for f in os.listdir(f"{settings.WORK_DIR}{cwd}")
            if os.path.isfile(os.path.join(f"{settings.WORK_DIR}{cwd}", f))
        ]
        dirs = [
            d
            for d in os.listdir(f"{settings.WORK_DIR}{cwd}")
            if os.path.isdir(os.path.join(f"{settings.WORK_DIR}{cwd}", d))
        ]
        return JsonResponse(
            {
                "msg": [
                    {"files": files},
                    {"directories": dirs},
                ]
            },
            status=200,
        )


def dir_make(name, cwd):
    if os.path.isdir(f"{settings.WORK_DIR}{cwd}"):
        return JsonResponse({"msg": {"error": "directory with such name already exists"}}, status=400)
    else:
        os.mkdir(f"{settings.WORK_DIR}{cwd}{name}")
        return HttpResponse(status=201)


def dir_delete(cwd):
    if not os.path.isdir(f"{settings.WORK_DIR}{cwd}"):
        return JsonResponse({"msg": {"error": "directory with such name already exists"}}, status=400)
    else:
        shutil.rmtree(f"{settings.WORK_DIR}{cwd}")
        return HttpResponse(status=200)
