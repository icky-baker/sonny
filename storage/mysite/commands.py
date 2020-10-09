import datetime
import logging
import os
import shutil
import time
from pathlib import Path

import requests
from django.conf import settings
from django.http import FileResponse, HttpResponse, JsonResponse

logger = logging.getLogger("common")


def init():
    shutil.rmtree(settings.WORK_DIR)
    os.mkdir(settings.WORK_DIR)
    _, _, free = shutil.disk_usage("/")  # Get free space
    logger.info("The initialization: done")
    return JsonResponse({"msg": {"available_size": free // (2 ** 30)}}, status=200)


def file_create(name, cwd):
    if os.path.isfile(f"{settings.WORK_DIR}{cwd}{name}"):
        return JsonResponse({"msg": {"error": "file with such name already exists"}}, status=400)
    else:
        with open(f"{settings.WORK_DIR}{cwd}{name}", "w+") as _:
            pass  # name host port cwd

        logger.info("The file: created")
        r = requests.post(
            f"{settings.HOST_NAMING}/api/file/approve/",
            data={
                "file": name,
                "access time": time.ctime(os.path.getatime(f"{settings.WORK_DIR}{cwd}{name}")),
                "modified time": time.ctime(os.path.getmtime(f"{settings.WORK_DIR}{cwd}{name}")),
                "change time": time.ctime(os.path.getctime(f"{settings.WORK_DIR}{cwd}{name}")),
                "size": os.path.getsize(f"{settings.WORK_DIR}{cwd}{name}"),
            },
            params={"name": name, "host": settings.HOST_IP, "port": settings.HOST_PORT, "cwd": cwd},
        )
        logger.info(f"Response from naming server: {r.status_code}")

        if r.json()["replicate_to"] is not None:
            host = r.json()["replicate_to"]["host"]
            port = r.json()["replicate_to"]["port"]
            r = requests.get(
                f"http://{host}:{port}/api/dfs/",
                params={"command": "file_create", "name": name, "cwd": cwd},
            )
            logger.info(f"Response from storage server-replica: {r.status_code}")

        return HttpResponse(status=201)


def file_read(name, cwd):
    if not os.path.isfile(f"{settings.WORK_DIR}{cwd}{name}"):
        return JsonResponse({"msg": {"error": "file with such name does not exists"}}, status=404)
    else:
        return FileResponse(open(f"{settings.WORK_DIR}{cwd}{name}", "rb"), as_attachment=True)


def file_write(request, cwd):
    def handle_uploaded_file(file, cwd):
        with open(f"{settings.WORK_DIR}{cwd}{file.name}", "wb+") as dest:
            for chunk in file.chunks():
                dest.write(chunk)

    file = request.FILES["file"]
    handle_uploaded_file(file=file, cwd=cwd)
    logger.info("The file: written")
    r = requests.post(
        f"{settings.HOST_NAMING}/api/file/approve/",
        data={
            "file": file.name,
            "access time": time.ctime(os.path.getatime(f"{settings.WORK_DIR}{cwd}{file.name}")),
            "modified time": time.ctime(os.path.getmtime(f"{settings.WORK_DIR}{cwd}{file.name}")),
            "change time": time.ctime(os.path.getctime(f"{settings.WORK_DIR}{cwd}{file.name}")),
            "size": file.size,
        },
        params={"name": file.name, "host": settings.HOST_IP, "port": settings.HOST_PORT, "cwd": cwd},
    )
    logger.info(f"Response from naming server: {r.status_code}")

    if r.json()["replicate_to"] is not None:
        host = r.json()["replicate_to"]["host"]
        port = r.json()["replicate_to"]["port"]
        r = requests.post(
            f"http://{host}:{port}/api/dfs/",
            files={"file": open(f"{settings.WORK_DIR}{cwd}{file.name}", "rb")},
            # data={"file": open(f"{settings.WORK_DIR}{cwd}{file.name}", "rb")},
            params={"command": "file_write", "cwd": cwd},
        )
        logger.info(f"Response from storage server-replica: {r.status_code}")

    return HttpResponse(status=200)


def file_delete(name, cwd):
    if not os.path.isfile(f"{settings.WORK_DIR}{cwd}{name}"):
        return JsonResponse({"msg": {"error": "file with such name does not exists"}}, status=404)
    else:
        os.remove(f"{settings.WORK_DIR}{cwd}{name}")
        logger.info("The file: deleted")
        r = requests.post(
            f"{settings.HOST_NAMING}/api/file/delete/",
            data={},
            params={"name": name, "host": settings.HOST_IP, "port": settings.HOST_PORT, "cwd": cwd},
        )
        logger.info(f"Response from naming server: {r.status_code}")

        if r.json()["replicate_to"] is not None:
            host = r.json()["replicate_to"]["host"]
            port = r.json()["replicate_to"]["port"]
            r = requests.get(
                f"http://{host}:{port}/api/dfs/",
                params={"command": "file_delete", "name": name, "cwd": cwd},
            )
            logger.info(f"Response from storage server-replica: {r.status_code}")

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
        logger.info("The file: copied")

        # r = requests.post(
        #     url=f"{settings.HOST_NAMING}/api/file/",
        #     headers={"Server-Hash": "suchsecret"},
        #     params={"name": target, "size": os.path.getsize(f"{settings.WORK_DIR}{cwd}{target}"), "cwd": cwd},
        # )
        # logger.info(f"Response from naming server to create file: {r.status_code}")

        r = requests.post(
            f"{settings.HOST_NAMING}/api/file/approve/",
            data={
                "file": target,
                "access time": time.ctime(os.path.getatime(f"{settings.WORK_DIR}{cwd}{target}")),
                "modified time": time.ctime(os.path.getmtime(f"{settings.WORK_DIR}{cwd}{target}")),
                "change time": time.ctime(os.path.getctime(f"{settings.WORK_DIR}{cwd}{target}")),
                "size": os.path.getsize(f"{settings.WORK_DIR}{cwd}{target}"),
            },
            params={"name": target, "host": settings.HOST_IP, "port": settings.HOST_PORT, "cwd": cwd},
        )
        logger.info(f"Response from naming server: {r.status_code}")

        if r.json()["replicate_to"] is not None:
            host = r.json()["replicate_to"]["host"]
            port = r.json()["replicate_to"]["port"]
            r = requests.get(
                f"http://{host}:{port}/api/dfs/",
                params={"command": "file_copy", "name": name, "cwd": cwd},
            )
            logger.info(f"Response from storage server-replica: {r.status_code}")

        return JsonResponse({"msg": {"filename": target}}, status=200)


def file_move(name, cwd, path):
    if not os.path.isfile(f"{settings.WORK_DIR}{cwd}{name}"):
        return JsonResponse({"msg": {"error": "file with such name does not exists"}}, status=404)
    else:
        if path[0] != "/":
            path = "/" + path
        if path[-1] != "/":
            path = path + "/"
        shutil.move(f"{settings.WORK_DIR}{cwd}{name}", f"{settings.WORK_DIR}{path}{name}")
        logger.info("The file: moved")
        r = requests.post(
            f"{settings.HOST_NAMING}/api/file/delete/",
            data={},
            params={"name": name, "host": settings.HOST_IP, "port": settings.HOST_PORT, "cwd": cwd},
        )
        logger.info(f"Response from naming server: {r.status_code}")

        # if r.json()["replicate_to"] is not None:
        #     host = r.json()["replicate_to"]["host"]
        #     port = r.json()["replicate_to"]["port"]
        #     r = requests.get(
        #         f"http://{host}:{port}/api/dfs/",
        #         params={"command": "file_delete", "name": name, "cwd": cwd},
        #     )
        #     logger.info(f"Response from storage server-replica: {r.status_code}")

        # r = requests.post(
        #     url=f"{settings.HOST_NAMING}/api/file/",
        #     headers={"Server-Hash": "suchsecret"},
        #     params={"name": name, "size": os.path.getsize(f"{settings.WORK_DIR}{path}{name}"), "cwd": cwd},
        # )
        # logger.info(f"Response from naming server to create file: {r.status_code}")

        r = requests.post(
            f"{settings.HOST_NAMING}/api/file/approve/",
            data={
                "file": name,
                "access time": time.ctime(os.path.getatime(f"{settings.WORK_DIR}{path}{name}")),
                "modified time": time.ctime(os.path.getmtime(f"{settings.WORK_DIR}{path}{name}")),
                "change time": time.ctime(os.path.getctime(f"{settings.WORK_DIR}{path}{name}")),
                "size": os.path.getsize(f"{settings.WORK_DIR}{path}{name}"),
            },
            params={"name": name, "host": settings.HOST_IP, "port": settings.HOST_PORT, "cwd": path},
        )
        logger.info(f"Response from naming server: {r.status_code}")

        if r.json()["replicate_to"] is not None:
            host = r.json()["replicate_to"]["host"]
            port = r.json()["replicate_to"]["port"]
            r = requests.get(
                f"http://{host}:{port}/api/dfs/",
                params={"command": "file_move", "name": name, "cwd": cwd, "path": path},
            )
            logger.info(f"Response from storage server-replica: {r.status_code}")

        return HttpResponse("The file is moved", status=200)


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
    if os.path.exists(f"{settings.WORK_DIR}{cwd}{name}"):
        return JsonResponse({"msg": {"error": "directory with such name already exists"}}, status=400)
    else:
        os.mkdir(f"{settings.WORK_DIR}{cwd}{name}")
        logger.info("The directory: created")
        r = requests.post(
            f"{settings.HOST_NAMING}/api/file/approve/",
            data={},
            params={"name": name, "host": settings.HOST_IP, "port": settings.HOST_PORT, "cwd": cwd},
        )
        logger.info(f"Response from naming server: {r.status_code}")

        if r.json()["replicate_to"] is not None:
            host = r.json()["replicate_to"]["host"]
            port = r.json()["replicate_to"]["port"]
            r = requests.get(
                f"http://{host}:{port}/api/dfs/",
                params={"command": "dir_make", "name": name, "cwd": cwd},
            )
            logger.info(f"Response from storage server-replica: {r.status_code}")

        return HttpResponse(status=201)


def dir_delete(cwd):
    if not os.path.exists(f"{settings.WORK_DIR}{cwd}"):
        return JsonResponse({"msg": {"error": "directory with such name doesn't exist"}}, status=400)
    else:
        shutil.rmtree(f"{settings.WORK_DIR}{cwd}")
        # NOTE: fuck the way how directory to delete is transferred between client and storage server
        # Because of there constrains, we need to extract real dir name here
        real_cwd = Path(cwd)
        dir_name = real_cwd.name
        real_cwd = real_cwd.parent

        logger.info("The directory: deleted")
        logger.info(f"{dir_name=}, {real_cwd=}")

        real_cwd = str(real_cwd)
        real_cwd = str(real_cwd) if real_cwd[-1] == "/" else str(real_cwd) + "/"

        r = requests.post(
            f"{settings.HOST_NAMING}/api/file/delete/",
            data={},
            params={"name": dir_name, "host": settings.HOST_IP, "port": settings.HOST_PORT, "cwd": real_cwd},
        )
        logger.info(f"Response from naming server: {r.status_code}")

        if r.json()["replicate_to"]:
            host = r.json()["replicate_to"]["host"]
            port = r.json()["replicate_to"]["port"]
            r = requests.get(
                f"http://{host}:{port}/api/dfs/",
                params={"command": "dir_delete", "cwd": cwd},
            )
            logger.info(f"Response from storage server-replica: {r.status_code}")

        return HttpResponse(status=200)
