import json
import os
import pathlib
import random
import socket
import sys
from typing import Optional

import requests
import tqdm
import typer

app = typer.Typer()
# IP = "3.134.152.50"
IP = "naming"
PORT = "80"
# get zapros file_create [command] [filename] [directory name]
# ip/api/dfs


BASE_DIR = pathlib.Path(__file__).parent.absolute() / "data"
SCRIPT_DIR = BASE_DIR.parent

# CWD = "/"  # should start and end with '/'
with open(f"{BASE_DIR}/data.json", "w") as json_file:
    try:
        CWD = json.load(json_file).get("cwd", "/")
    except ValueError:
        CWD = "/"


def data_dump():
    with open(f"{BASE_DIR}/data.json", "w") as out:
        json.dump({"cwd": CWD}, out, indent=4)


@app.command()
def initialize():
    # Initialize the client storage on a new system, should remove any existing file in the dfs root directory and return available size.

    r = requests.post(url="http://" + IP + ":" + PORT + "/api/hosts/", headers={"Server-Hash": "suchsecret"})
    total_available_space = 0
    for host in r.json()["hosts"]:
        requests.get(
            url="http://" + str(host["host"]) + ":" + str(host["port"]) + "/api/dfs/",
            params={"command": "init", "cwd": CWD},
        )

        ip, space = host["host"], host["available_space"]
        total_available_space += space
        typer.echo(f"Host {ip} : {space} bytes available")

    typer.echo(f"\nTotal {total_available_space} available")
    data_dump()


@app.command()
def file_create(filename: str):
    # Should allow to create a new empty file.

    r = requests.post(
        url="http://" + IP + ":" + PORT + "/api/file/",
        params={"name": filename, "size": 1, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )

    storage_ip, storage_port = str(r.json()["hosts"][0]["host"]), str(r.json()["hosts"][0]["port"])
    print(storage_ip, storage_port)

    r = requests.get(
        url="http://" + storage_ip + ":" + storage_port + "/api/dfs/",
        params={"command": "file_create", "name": filename, "cwd": CWD},
    )
    typer.echo(r.content)
    data_dump()


@app.command()
def file_read(filename: str):
    # Should allow to read any file from DFS (download a file from the DFS to the Client side).
    r = requests.get(
        url="http://" + IP + ":" + PORT + "/api/file/",
        params={"name": filename, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )

    storage_ip, storage_port = str(r.json()[0]["host"]), str(r.json()[0]["port"])
    r = requests.get(
        url="http://" + storage_ip + ":" + storage_port + "/api/dfs/",
        params={"command": "file_read", "name": filename, "cwd": CWD},
    )
    if r.status_code == 200:
        with open(os.path.join(BASE_DIR, filename), "wb+") as fp:
            print(r.content)
            fp.write(r.content)
    else:
        typer.echo("Che-to ne tak. File ne zagruzilsya")
    pass
    data_dump()


@app.command()
def file_write(path_to_the_file: str):
    # Should allow to put any file to DFS (upload a file from the Client side to the DFS)

    size = os.path.getsize(SCRIPT_DIR / path_to_the_file)  # in bytes
    filename = SCRIPT_DIR / path_to_the_file
    # filename = path_to_the_file[path_to_the_file.rindex("/") + 1 :]
    # typer.echo(size)
    # typer.echo(path_to_the_file[path_to_the_file.rindex('/')+1:])

    r = requests.post(
        url="http://" + IP + ":" + PORT + "/api/file/",
        params={"name": filename, "size": size, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )
    typer.echo(r.content)

    typer.echo(f"Uploading the file {filename} to the server")
    storage_ip, storage_port = str(r.json()["hosts"][0]["host"]), str(r.json()["hosts"][0]["port"])
    url = "http://" + storage_ip + ":" + storage_port + "/api/dfs/"
    files = {"file": open(filename, "rb")}
    # values = {"file": open(filename, "rb")}  # filename}
    values = {}
    # Данил: post
    # в теле - key="file", value - файл
    params = {"command": "file_write", "name": filename, "cwd": CWD}
    r = requests.post(url=url, files=files, data=values, params=params)
    if r.status_code == 200:
        typer.echo(f"{filename} is uploaded successfully!")
    else:
        typer.echo(r.content)
    data_dump()
    # post
    # в теле - key="file", value - файл


@app.command()
def file_delete(filename: str):
    # Should allow to delete any file from DFS

    r = requests.get(
        url="http://" + IP + ":" + PORT + "/api/file/",
        params={"name": filename, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )
    typer.echo(r.content)

    if r.json()["hosts"]:
        storage_ip, storage_port = str(r.json()["hosts"][0]["host"]), str(r.json()["hosts"][0]["port"])

        r = requests.get(
            url="http://" + storage_ip + ":" + storage_port + "/api/dfs/",
            params={"command": "file_delete", "name": filename, "cwd": CWD},
        )
    else:
        typer.echo("Such file doesn't exist")
    data_dump()


@app.command()
def file_info(filename: str):
    # Should provide information about the file (any useful information - size, node id, etc.)

    r = requests.get(
        url="http://" + IP + ":" + PORT + "/api/file/",
        params={"name": filename, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )
    if r.status_code == 404:
        typer.echo("Such file doesn't exist")
        return

    typer.echo(r.content)
    # TODO: beautiful print of file info
    # {"hosts": [{"host": "192.168.224.4", "port": 8000}], "file_info": {"file": "canvas.png", "size": "12345922", "access time": "Tue Oct  6 22:32:57 2020", "change time": "Tue Oct  6 22:32:57 2020", "modified time": "Tue Oct  6 22:32:57 2020"}}
    data_dump()


@app.command()
def file_copy(filename: str):
    # Should allow to create a copy of file.

    r = requests.get(
        url="http://" + IP + ":" + PORT + "/api/file/",
        params={"name": filename, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )

    storage_ip, storage_port = str(r.json()["hosts"][0]["host"]), str(r.json()["hosts"][0]["port"])
    r = requests.get(
        url="http://" + storage_ip + ":" + storage_port + "/api/dfs/",
        params={"command": "file_copy", "name": filename, "cwd": CWD},
    )
    typer.echo(r.text)
    data_dump()


@app.command()
def file_move(filename: str, destination_path: str):
    # Should allow to move a file to the specified path.
    r = requests.get(
        url="http://" + IP + ":" + PORT + "/api/file/",
        params={"name": filename, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )

    storage_ip, storage_port = str(r.json()["hosts"][0]["host"]), str(r.json()["hosts"][0]["port"])
    r = requests.get(
        url="http://" + storage_ip + ":" + storage_port + "/api/dfs/",
        params={"command": "file_move", "name": filename, "cwd": CWD, "path": destination_path},
    )
    data_dump()


@app.command()
def open_directory(name: str):
    # Should allow to change directory

    global CWD

    r = requests.get(
        url="http://" + IP + ":" + PORT + "/api/directory/",
        params={"name": name, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )

    if r.status_code == 200:
        if name == "..":
            CWD = CWD[CWD.rfind("/") + 1 :]
        else:
            CWD += name + "/"
        typer.echo(f"Current working directory is {CWD}")
    else:
        typer.echo("Such directory doesn't exist")
    data_dump()


@app.command()
def read_directory(path: Optional[str] = typer.Argument(CWD)):
    # Should return list of files, which are stored in the directory.
    r = requests.get(
        url="http://" + IP + ":" + PORT + "/api/directory/",
        params={"name": path, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )
    data_dump()
    r_json = r.json()  # noqa
    # b'{"files": [{"id": 1, "name": "/dd", "size": null, "meta": {}, "hosts": [{"id": 1, "host": "172.26.0.4", "port": 8000, "status": "RUNNING", "available_space": 52596977664}, {"id": 2, "host": "172.26.0.6", "port": 8000, "status": "RUNNING", "available_space": 52596957184}, {"id": 3, "host": "172.26.0.5", "port": 8000, "status": "RUNNING", "available_space": 52596953088}]}, {"id": 2, "name": "/dd2", "size": null, "meta": {}, "hosts": [{"id": 1, "host": "172.26.0.4", "port": 8000, "status": "RUNNING", "available_space": 52596977664}, {"id": 2, "host": "172.26.0.6", "port": 8000, "status": "RUNNING", "available_space": 52596957184}, {"id": 3, "host": "172.26.0.5", "port": 8000, "status": "RUNNING", "available_space": 52596953088}]}, {"id": 3, "name": "/dd3", "size": null, "meta": {}, "hosts": [{"id": 1, "host": "172.26.0.4", "port": 8000, "status": "RUNNING", "available_space": 52596977664}, {"id": 2, "host": "172.26.0.6", "port": 8000, "status": "RUNNING", "available_space": 52596957184}, {"id": 3, "host": "172.26.0.5", "port": 8000, "status": "RUNNING", "available_space": 52596953088}]}, {"id": 4, "name": "/dd/canvas.png", "size": 12345922, "meta": {"file": "canvas.png", "size": "12345922", "access time": "Tue Oct  6 23:18:25 2020", "change time": "Tue Oct  6 23:18:25 2020", "modified time": "Tue Oct  6 23:18:25 2020"}, "hosts": [{"id": 1, "host": "172.26.0.4", "port": 8000, "status": "RUNNING", "available_space": 52596977664}, {"id": 2, "host": "172.26.0.6", "port": 8000, "status": "RUNNING", "available_space": 52596957184}, {"id": 3, "host": "172.26.0.5", "port": 8000, "status": "RUNNING", "available_space": 52596953088}]}]}'

    # TODO: нужно выводить инфу из запроса к неймингу
    # пример есть в комментарии наверху
    # если size None - то это директория, иначе - файл


@app.command()
def make_directory(directory_name: str, path: Optional[str] = None):
    if not path:
        path = CWD

    # Should allow to create a new directory.
    r = requests.post(url="http://" + IP + ":" + PORT + "/api/hosts/", headers={"Server-Hash": "suchsecret"})
    storage_server = random.randint(0, len(r.json()["hosts"]) - 1)
    storage_ip, storage_port = str(r.json()["hosts"][storage_server]["host"]), str(
        r.json()["hosts"][storage_server]["port"]
    )

    r = requests.get(
        url="http://" + storage_ip + ":" + storage_port + "/api/dfs/",
        params={"command": "dir_make", "cwd": path, "name": directory_name},
    )

    typer.echo(f"Created directory {path}{directory_name}/")
    data_dump()


@app.command()
def delete_directory(directory_name: str, path: Optional[str] = None):
    if not path:
        path = CWD

    # Should allow to delete directory.  If the directory contains files the system should ask for confirmation from the user before deletion.
    r = requests.post(url="http://" + IP + ":" + PORT + "/api/hosts/", headers={"Server-Hash": "suchsecret"})
    storage_server = random.randint(0, len(r.json()["hosts"]) - 1)
    storage_ip, storage_port = str(r.json()["hosts"][storage_server]["host"]), str(
        r.json()["hosts"][storage_server]["port"]
    )

    r = requests.get(
        url="http://" + storage_ip + ":" + storage_port + "/api/dfs/",
        params={"command": "dir_delete", "cwd": f"{path}{directory_name}"},
    )

    if r.status_code == 200:
        typer.echo(r.text)
    elif r.status_code == 400:
        typer.echo("Directory with such name doesn't exist")
    data_dump()


if __name__ == "__main__":
    app()
