import json
import os
import shutil
from random import choice

import requests
from django.conf import settings


def recovery(resp):
    for item in resp:
        item = json.loads(item)

        name = item.get("name", None)
        size = item.get("size", None)
        hosts = item.get("hosts", None)
        # hosts = [d['value'] for d in l]

        if size is not None:  # if this is a file
            if os.path.isfile(f"{settings.WORK_DIR}{name}"):
                if len(hosts) == 0:  # A file only on this server
                    os.remove(f"{settings.WORK_DIR}{name}")
            else:  # A file doesn't exists on this server
                host = choice(hosts)
                r = requests.get(
                    f"http://{host.get('host')}:{host.get('port')}/api/dfs/",
                    params={"command": "file_read", "name": name[1::], "cwd": "/"},
                )
                if r.status_code == 200:
                    with open(name, "wb+") as fp:
                        fp.write(r.content)

        else:  # if this is a directory
            pass


def registry(host_naming, host_ip, host_port):
    _, _, free_space = shutil.disk_usage("/")
    r = requests.get(
        f"{host_naming}/api/server/register/",
        params={"space": free_space, "host": host_ip, "port": host_port},
    )
    print(f"Response from naming server: {r.status_code}")

    print(json.loads(r.text).get("files", []))


def create_workdir(workdir):
    try:
        os.mkdir(workdir)
    except OSError:
        print("Working directory already exists")
    else:
        print("Successfully created the working directory")
