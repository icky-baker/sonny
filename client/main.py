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
from beautifultable import BeautifulTable
from pathvalidate import ValidationError, validate_filename, validate_filepath

app = typer.Typer()
if os.getenv("IS_IN_DOCKER"):
    IP = "naming"
else:
    IP = "3.134.152.50"
PORT = "80"
# get zapros file_create [command] [filename] [directory name]
# ip/api/dfs


BASE_DIR = pathlib.Path(__file__).parent.absolute() / "data"
SCRIPT_DIR = BASE_DIR.parent


try:
    with open(f"{BASE_DIR}/data.json", "r") as json_file:
        CWD = json.load(json_file)["cwd"]
except (json.decoder.JSONDecodeError, FileNotFoundError):
    CWD = "/"


def data_dump(cwd: Optional[str] = None):
    if not cwd:
        cwd = CWD

    with open(f"{BASE_DIR}/data.json", "w") as out:
        json.dump({"cwd": cwd}, out, indent=4)


@app.command()
def initialize():
    # Initialize the client storage on a new system, should remove any existing file in the dfs root directory and return available size.

    typer.echo("Initializing")
    r = requests.get(url="http://" + IP + ":" + PORT + "/api/init/", headers={"Server-Hash": "suchsecret"})

    r = requests.post(url="http://" + IP + ":" + PORT + "/api/hosts/", headers={"Server-Hash": "suchsecret"})
    if not (r.status_code == 200 and len(r.json()["hosts"]) > 0):
        typer.echo(f"\nTotal {0} bytes available")
        return

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

    data_dump("/")


@app.command()
def file_create(filename: str):
    # Should allow to create a new empty file.

    try:
        validate_filename(filename)
    except ValidationError as e:
        typer.echo(f"{e}\n", file=sys.stderr)

    r = requests.post(
        url="http://" + IP + ":" + PORT + "/api/file/",
        params={"name": filename, "size": 1, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )

    if r.status_code != 200:
        typer.echo(f"Error {r.status_code} {r.text}")
        return
    storage_ip, storage_port = str(r.json()["hosts"][0]["host"]), str(r.json()["hosts"][0]["port"])
    typer.echo(f"Creating file '{filename}' on server '{storage_ip}'")

    req = requests.get(
        url="http://" + storage_ip + ":" + storage_port + "/api/dfs/",
        params={"command": "file_create", "name": filename, "cwd": CWD},
    )

    if req.status_code == 201:
        typer.echo(f"File '{filename}' is successfilly created")
    else:
        typer.echo(f"Error {req.status_code} \n File with this name already exists")

    data_dump()


@app.command()
def file_read(filename: str):
    # Should allow to read any file from DFS (download a file from the DFS to the Client side).
    try:
        validate_filename(filename)
    except ValidationError as e:
        typer.echo(f"{e}\n", file=sys.stderr)

    r = requests.get(
        url="http://" + IP + ":" + PORT + "/api/file/",
        params={"name": filename, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )

    if r.status_code != 200:
        typer.echo(f"Error {r.status_code} {r.text}")
        return

    storage_ip, storage_port = str(r.json()["hosts"][0]["host"]), str(r.json()["hosts"][0]["port"])
    req = requests.get(
        url="http://" + storage_ip + ":" + storage_port + "/api/dfs/",
        params={"command": "file_read", "name": filename, "cwd": CWD},
    )
    if req.status_code != 200:
        typer.echo(f"Error {req.status_code} {req.text}")
        return

    typer.echo(f"Downloading the file {filename} from the server")
    with open(os.path.join(BASE_DIR, filename), "wb+") as fp:
        fp.write(req.content)
    typer.echo(f"File '{filename}' is downloaded")

    data_dump()


@app.command()
def file_write(path_to_the_file: str):
    # Should allow to put any file to DFS (upload a file from the Client side to the DFS)

    try:
        validate_filepath(path_to_the_file)
    except ValidationError as e:
        typer.echo(f"{e}\n", file=sys.stderr)

    size = os.path.getsize(SCRIPT_DIR / path_to_the_file)  # in bytes
    filename = SCRIPT_DIR / path_to_the_file

    r = requests.post(
        url="http://" + IP + ":" + PORT + "/api/file/",
        params={"name": pathlib.Path(filename).name, "size": size, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )

    if r.status_code != 200:
        typer.echo(f"Error {r.status_code} {r.text}")
        return

    storage_ip, storage_port = str(r.json()["hosts"][0]["host"]), str(r.json()["hosts"][0]["port"])
    typer.echo(f"Uploading the file {filename} to the server {storage_ip}")
    url = "http://" + storage_ip + ":" + storage_port + "/api/dfs/"
    files = {"file": open(filename, "rb")}
    params = {"command": "file_write", "name": filename, "cwd": CWD}
    req = requests.post(url=url, files=files, params=params)

    if req.status_code != 200:
        typer.echo(f"Error {req.status_code} {req.text}")
        return
    typer.echo(f"{filename} is uploaded successfully!")

    data_dump()


@app.command()
def file_delete(filename: str):
    # Should allow to delete any file from DFS

    try:
        validate_filename(filename)
    except ValidationError as e:
        typer.echo(f"{e}\n", file=sys.stderr)

    r = requests.get(
        url="http://" + IP + ":" + PORT + "/api/file/",
        params={"name": filename, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )

    if r.status_code != 200:
        typer.echo(f"Error {r.status_code} {r.text}")
        return

    storage_ip, storage_port = str(r.json()["hosts"][0]["host"]), str(r.json()["hosts"][0]["port"])
    typer.echo(f"Deleting the file {filename} from the server {storage_ip}")
    req = requests.get(
        url="http://" + storage_ip + ":" + storage_port + "/api/dfs/",
        params={"command": "file_delete", "name": filename, "cwd": CWD},
    )

    if req.status_code == 200:
        typer.echo(f"{filename} is deleted successfully!")
    else:
        typer.echo(f"Error {req.status_code} {req.text}")

    data_dump()


@app.command()
def file_info(filename: str):
    # Should provide information about the file (any useful information - size, node id, etc.)

    try:
        validate_filename(filename)
    except ValidationError as e:
        typer.echo(f"{e}\n", file=sys.stderr)

    r = requests.get(
        url="http://" + IP + ":" + PORT + "/api/file/",
        params={"name": filename, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )
    if r.status_code == 404:
        typer.echo("File with this name doesn't exist")
        return

    info = r.json()["file_info"]

    table = BeautifulTable()
    print("keys are", info.keys())
    table.columns.header = list(map(str, info.keys()))
    table.rows.append(map(str, info.values()))
    typer.echo(str(table))

    data_dump()


@app.command()
def file_copy(filename: str):
    # Should allow to create a copy of file.

    try:
        validate_filename(filename)
    except ValidationError as e:
        typer.echo(f"{e}\n", file=sys.stderr)

    r = requests.get(
        url="http://" + IP + ":" + PORT + "/api/file/",
        params={"name": filename, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )

    if r.status_code != 200:
        typer.echo(f"Error {r.status_code} {r.text}")
        return

    storage_ip, storage_port = str(r.json()["hosts"][0]["host"]), str(r.json()["hosts"][0]["port"])
    typer.echo("File replication is in process")
    r = requests.get(
        url="http://" + storage_ip + ":" + storage_port + "/api/dfs/",
        params={"command": "file_copy", "name": filename, "cwd": CWD},
    )

    if r.status_code != 200:
        typer.echo(f"Error {r.status_code} {r.text}")
        return

    typer.echo(f"File '{filename}' is successfully copied'")
    data_dump()


@app.command()
def file_move(filename: str, destination_path: str):
    # Should allow to move a file to the specified path.

    try:
        validate_filename(filename)
    except ValidationError as e:
        typer.echo(f"{e}\n", file=sys.stderr)

    try:
        validate_filepath(destination_path)
    except ValidationError as e:
        typer.echo(f"{e}\n", file=sys.stderr)

    r = requests.get(
        url="http://" + IP + ":" + PORT + "/api/file/",
        params={"name": filename, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )

    if r.status_code != 200:
        typer.echo(f"Error {r.status_code} {r.text}")
        return

    storage_ip, storage_port = str(r.json()["hosts"][0]["host"]), str(r.json()["hosts"][0]["port"])
    typer.echo(f"File transfer to '{destination_path}' is in process")
    r = requests.get(
        url="http://" + storage_ip + ":" + storage_port + "/api/dfs/",
        params={"command": "file_move", "name": filename, "cwd": CWD, "path": destination_path},
    )

    if r.status_code != 200:
        typer.echo(f"Error {r.status_code} {r.text}")
        return

    typer.echo(f"File '{filename}' is successfully transfered'")
    data_dump()


@app.command()
def open_directory(name: str):
    # Should allow to change directory
    if (name!=".."):
        try:
            validate_filepath(name)
        except ValidationError as e:
            typer.echo(f"{e}\n", file=sys.stderr)

    global CWD

    r = requests.get(
        url="http://" + IP + ":" + PORT + "/api/directory/",
        params={"name": name, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )

    if r.status_code == 200:
        real_cwd = pathlib.Path(CWD)
        cwd_by_name = {
            "..": real_cwd.parent,
            ".": real_cwd,
        }
        CWD = str(cwd_by_name.get(name, real_cwd / name))
        if CWD[-1] != "/":
            CWD += "/"

        data_dump(CWD)
        typer.echo(f"Current working directory is {CWD}")
    else:
        typer.echo(f"Error {r.status_code} \nSuch directory doesn't exist")


@app.command()
def ls():
    read_directory()


@app.command()
def read_directory():
    # Should return list of files, which are stored in the directory.
    # if not path:
    #     path = CWD
    # else:
    #     try:
    #         validate_filepath(path)
    #     except ValidationError as e:
    #         typer.echo(f"{e}\n", file=sys.stderr)
    #         return

    r = requests.get(
        url="http://" + IP + ":" + PORT + "/api/directory/",
        params={"name": ".", "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )
    data_dump()

    # r_json = r.json()
    # print(r.text)
    # print(r.status_code)
    respon_json = json.loads(r.text).get("files", [])

    files = []
    dirs = []
    for item in respon_json:
        name = item.get("name")
        size = item.get("size")
        (dirs if size is None else files).append(pathlib.Path(name).name + "/")
        # if size is None:
        #     dirs.append(name)
        # else:
        #     files.append(name)

    typer.echo(f"Current directory is {CWD}")
    if not files and not dirs:
        typer.echo("This directory is empty")
    else:
        msg = "Directory content:\n"
        if files:
            msg += "\tFiles:\n{}".format("\n".join(map(lambda s: f"\t\t- {s}", files)))
        if dirs:
            msg += "\tDirectories:\n{}".format("\n".join(map(lambda s: f"\t\t- {s}", dirs)))

        typer.echo(msg)


@app.command()
def make_directory(directory_name: str, path: Optional[str] = None):
    # Should allow to create a new directory.
    if not path:
        path = CWD
    else:
        try:
            validate_filepath(path)
        except ValidationError as e:
            typer.echo(f"{e}\n", file=sys.stderr)
            return

    r = requests.post(url="http://" + IP + ":" + PORT + "/api/hosts/", headers={"Server-Hash": "suchsecret"})
    storage_server = random.randint(0, len(r.json()["hosts"]) - 1)
    storage_ip, storage_port = str(r.json()["hosts"][storage_server]["host"]), str(
        r.json()["hosts"][storage_server]["port"]
    )
    if r.status_code != 200:
        typer.echo(f"Error {r.status_code} {r.text}")
        return

    r = requests.get(
        url="http://" + storage_ip + ":" + storage_port + "/api/dfs/",
        params={"command": "dir_make", "cwd": path, "name": directory_name},
    )
    if r.status_code != 201:
        typer.echo(f"Error {r.status_code} {r.text}")
        return

    typer.echo(f"Created directory {path}{directory_name}/")
    data_dump()


@app.command()
def rmdir(directory_name: str):
    delete_directory(directory_name)

@app.command()
def mkdir(directory_name: str):
    make_directory(directory_name)


@app.command()
def delete_directory(directory_name: str):
    path = None
    not_allowed_names = ["..", "."]
    if directory_name in not_allowed_names:
        typer.echo("I can't delete this directory")
        return

    # Should allow to delete directory.  If the directory contains files the system should ask for confirmation from the user before deletion.
    if not path:
        path = CWD
    else:
        try:
            validate_filepath(path)
        except ValidationError as e:
            typer.echo(f"{e}\n", file=sys.stderr)
            return

    r = requests.get(
        url="http://" + IP + ":" + PORT + "/api/directory/",
        params={"name": directory_name, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )
    # typer.echo(r.text)

    respon_json = json.loads(r.text).get("files", [])

    if len(respon_json) != 0:
        files = []
        dirs = []
        for item in respon_json:
            name = item.get("name")
            size = item.get("size")
            if size is None:
                dirs.append(name)
            else:
                files.append(name)

        typer.echo(
            "This directory is not empty \n\nFiles:\n\n{}\nDirectories:\n\n{}\n".format(
                "\n".join(files), "\n".join(dirs)
            )
        )
        delete = typer.confirm("Are you sure you want to delete it?")
        if not delete:
            typer.echo("Not deleting")
            raise typer.Abort()
        typer.echo("Deleting it!")

    r = requests.get(
        url="http://" + IP + ":" + PORT + "/api/file/",
        params={"name": directory_name, "cwd": CWD},
        headers={"Server-Hash": "suchsecret"},
    )

    server = random.choice(r.json()["hosts"])
    storage_ip, storage_port = server["host"], str(server["port"])

    if r.status_code != 200:
        typer.echo(f"Error {r.status_code} {r.text}")
        return

    r = requests.get(
        url="http://" + storage_ip + ":" + storage_port + "/api/dfs/",
        params={"command": "dir_delete", "cwd": f"{path}{directory_name}"},
    )

    if r.status_code == 200:
        typer.echo("Directory is succesfully deleted")
    elif r.status_code == 400:
        typer.echo("Directory with such name doesn't exist")
    data_dump()


@app.command()
def pwd():
    typer.echo(CWD)


if __name__ == "__main__":
    app()
