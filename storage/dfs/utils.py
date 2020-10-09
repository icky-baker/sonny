import json
import logging
import os
import shutil
from random import choice

import requests
from django.conf import settings

logger = logging.getLogger("common")


def recovery(resp):
    for item in resp:
        # item = json.loads(item)

        name = item.get("name", None)
        size = item.get("size", None)
        hosts = item.get("hosts", None)

        if name is None or hosts is None:
            logger.info(f"Incorrect values. Name={name}, Hosts={hosts}.")
            continue

        if size is not None:  # If this is a file
            if os.path.isfile(f"{settings.WORK_DIR}{name}"):
                if not hosts:  # A file only on this server
                    os.remove(f"{settings.WORK_DIR}{name}")
            else:  # A file doesn't exist on this server
                if hosts:
                    host = choice(hosts)  # Get random host
                    r = requests.get(
                        f"http://{host.get('host')}:{host.get('port')}/api/dfs/",
                        params={"command": "file_read", "name": name[1::], "cwd": "/"},
                    )
                    if r.status_code == 200:
                        with open(f"{settings.WORK_DIR}{name}", "wb+") as fp:
                            fp.write(r.content)

        else:  # If this is a directory
            if name == "/":
                continue
            # if os.path.isdir(name):
            if os.path.exists(f"{settings.WORK_DIR}{name}"):
                # NOTE: special case for the root directorry
                if not hosts:  # A directory only on this server
                    shutil.rmtree(f"{settings.WORK_DIR}{name}")
            else:
                os.mkdir(f"{settings.WORK_DIR}{name}")


def registry(host_naming, host_ip, host_port):
    _, _, free_space = shutil.disk_usage("/")
    r = requests.get(
        f"{host_naming}/api/server/register/",
        params={"space": free_space, "host": host_ip, "port": host_port},
    )
    logger.info(f"Response from naming server: {r.status_code}")

    recovery(json.loads(r.text).get("files", []))

    _, _, free_space = shutil.disk_usage("/")
    r = requests.get(
        f"{host_naming}/api/server/approve/",
        params={"space": free_space, "host": host_ip, "port": host_port},
    )


def create_workdir(workdir):
    try:
        os.mkdir(workdir)
    except OSError:
        logger.info("Working directory already exists")
    else:
        logger.info("Successfully created the working directory")
