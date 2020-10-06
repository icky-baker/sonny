import socket
import os
import tqdm
import sys
import requests
import typer
import random
from typing import Optional

app = typer.Typer()
IP = "3.134.152.50"
PORT = "80"
#get zapros file_create [command] [filename] [directory name]
#ip/api/dfs

CWD = '/'  #should start and end with '/'

@app.command()
def initialize():
# Initialize the client storage on a new system, should remove any existing file in the dfs root directory and return available size.

    r = requests.post(url="http://"+IP+':'+PORT+"/api/hosts/", 
                      headers={"Server-Hash":"suchsecret"})
    total_available_space = 0
    for host in r.json()["hosts"]:
        ip, space = host["host"], host["available_space"]
        total_available_space += space
        ip, space = host["host"], host["available_space"]
        typer.echo(f"Host {ip} : {space} bytes available")
    
    typer.echo(f"\nTotal {total_available_space} available")


@app.command()
def file_create(filename: str):
# Should allow to create a new empty file.

    r = requests.post(url="http://"+IP+':'+PORT+"/api/file/", 
                      params = {"name":filename,"size":1,"cwd":CWD},
                      headers={"Server-Hash":"suchsecret"})

    storage_ip, storage_port = r.json()["hosts"][0]["host"], r.json()["hosts"][0]["port"]
    print(storage_ip, storage_port)
    
    r = requests.get(url="http://"+storage_ip+':'+storage_port+"/api/dfs/", 
                     params = {"command":"file_create","name":filename, "cwd":CWD})
    typer.echo(r.content)

@app.command()
def file_read(filename: str):
#Should allow to read any file from DFS (download a file from the DFS to the Client side).
    r = requests.get(url = "http://"+IP+':'+PORT+"/api/file/", 
                    params = {"name":filename,"cwd":CWD},
                    headers={"Server-Hash":"suchsecret"})

    storage_ip, storage_port = r.json()["hosts"][0]["host"], r.json()["hosts"][0]["port"]
    r = requests.get(url="http://"+storage_ip+':'+storage_port+"/api/dfs/", 
                     params = {"command":"file_read","name":filename, "cwd":CWD})
    if (r.status_code == 200):
        with open(os.path.join(CWD, file), 'w') as fp:
            print(r.content)
            fp.write(r.content)
    else:
        typer.echo(f"Che-to ne tak. File ne zagruzilsya")
    pass

@app.command()
def file_write(path_to_the_file: str):
#Should allow to put any file to DFS (upload a file from the Client side to the DFS)
    
    size = os.path.getsize(path_to_the_file) #in bytes
    filename = path_to_the_file[path_to_the_file.rindex('/')+1:]
    # typer.echo(size)
    # typer.echo(path_to_the_file[path_to_the_file.rindex('/')+1:])
    
    r = requests.post(url="http://"+IP+':'+PORT+"/api/file/", 
                      params = {"name":filename,"size":size,"cwd":CWD}, 
                      headers={"Server-Hash":"suchsecret"})
    typer.echo(r.content)
  
    typer.echo(f"Uploading the file {filename} to the server")
    storage_ip, storage_port = r.json()["hosts"][0]["host"], r.json()["hosts"][0]["port"]
    url="http://"+storage_ip+':'+storage_port+"/api/dfs/"
    files={'files': open(filename,'rb')}
    values={'file' : open(filename,'rb')}#filename}
    #Данил: post
    #в теле - key="file", value - файл
    params = {"command":"file_write","name":filename,"cwd":CWD}
    r=requests.post(url=url,
                    files=files,
                    data=values,
                    params=params)
    if (r.status_code == 200):
        typer.echo(f"{filename} is uploaded successfully!")
    else:
        typer.echo(r.content)

    #post
    #в теле - key="file", value - файл

@app.command()
def file_delete(filename:str):
# Should allow to delete any file from DFS

    r = requests.get(url = "http://"+IP+':'+PORT+"/api/file/", 
                    params = {"name":filename, "cwd":CWD},
                    headers={"Server-Hash":"suchsecret"})
    typer.echo(r.content)
    
    storage_ip, storage_port = r.json()["hosts"][0]["host"], r.json()["hosts"][0]["port"]

    r = requests.get(url="http://"+storage_ip+':'+storage_port+"/api/dfs/", 
                     params = {"command":"file_delete","name":filename, "cwd":CWD})


@app.command()
def file_info(filename:str):
# Should provide information about the file (any useful information - size, node id, etc.)
    
    r = requests.get(url = "http://"+IP+':'+PORT+"/api/file/", 
                    params = {"name":filename, "cwd":CWD},
                    headers={"Server-Hash":"suchsecret"})

    typer.echo(r.text)


@app.command()
def file_copy(filename:str):
# Should allow to create a copy of file.

    r = requests.get(url = "http://"+IP+':'+PORT+"/api/file/", 
                    params = {"name":filename, "cwd":CWD},
                    headers={"Server-Hash":"suchsecret"})

    storage_ip, storage_port = r.json()["hosts"][0]["host"], r.json()["hosts"][0]["port"]
    r = requests.get(url="http://"+storage_ip+':'+storage_port+"/api/dfs/", 
                     params = {"command":"file_copy","name":filename, "cwd":CWD})
    typer.echo(r.text)

@app.command()
def file_move(filename:str, destination_path:str):
# Should allow to move a file to the specified path.
    r = requests.get(url = "http://"+IP+':'+PORT+"/api/file/", 
                    params = {"name":filename, "cwd":CWD},
                    headers={"Server-Hash":"suchsecret"})

    storage_ip, storage_port = r.json()["hosts"][0]["host"], r.json()["hosts"][0]["port"]
    r = requests.get(url="http://"+storage_ip+':'+storage_port+"/api/dfs/", 
                     params = {"command":"file_move","name":filename, "cwd":CWD, "path":destination_path})
    

@app.command()
def open_directory(name:str):
# Should allow to change directory

    global CWD
    #тут надо проверку на валидность name
    r = requests.get(url = "http://"+IP+':'+PORT+"/api/directory/", 
                    params = {"name":name, "cwd":CWD},
                    headers={"Server-Hash":"suchsecret"})
    storage_ip, storage_port = r.json()["hosts"][0]["host"], r.json()["hosts"][0]["port"]
    
    r = requests.get(url="http://"+storage_ip+':'+storage_port+"/api/dfs/", 
                     params = {"command":"open_directory","name":name, "cwd":CWD})
    if (r.status_code==200):
        if(name=='..'):
            CWD = CWD[CWD.rfind('/')+1:]
        else:
            CWD += (name+'/')

    

@app.command()
def read_directory(path:Optional[str] = typer.Argument("current working directory")):
# Should return list of files, which are stored in the directory.
    r = requests.get(url = "http://"+IP+':'+PORT+"/api/directory/", 
                    params = {"name":path, "cwd":CWD},
                    headers={"Server-Hash":"suchsecret"})
    storage_ip, storage_port = r.json()["hosts"][0]["host"], r.json()["hosts"][0]["port"]
    
    r = requests.get(url="http://"+storage_ip+':'+storage_port+"/api/dfs/", 
                     params = {"command":"read_directory", "cwd":path})
    typer.echo(r.text)

@app.command()
def make_directory(directory_name:str, path:Optional[str] = typer.Argument(CWD)):
# Should allow to create a new directory.
    r = requests.post(url="http://"+IP+':'+PORT+"/api/hosts/", 
                      headers={"Server-Hash":"suchsecret"})
    storage_server = random.randint(0,len(r.json()["hosts"])-1)
    storage_ip, storage_port = r.json()["hosts"][storage_server]["host"], r.json()["hosts"][storage_server]["port"]

    r = requests.get(url="http://"+storage_ip+':'+storage_port+"/api/dfs/", 
                     params = {"command":"make_directory", "cwd":path, "name":directory_name})

@app.command()
def delete_directory(path:Optional[str] = typer.Argument(CWD)):
#Should allow to delete directory.  If the directory contains files the system should ask for confirmation from the user before deletion. 
    r = requests.post(url="http://"+IP+':'+PORT+"/api/hosts/", 
                      headers={"Server-Hash":"suchsecret"})
    storage_server = random.randint(0,len(r.json()["hosts"])-1)
    storage_ip, storage_port = r.json()["hosts"][storage_server]["host"], r.json()["hosts"][storage_server]["port"]
    
    r = requests.get(url="http://"+storage_ip+':'+storage_port+"/api/dfs/", 
                     params = {"command":"delete_directory", "cwd":path})

    typer.echo(r.text)

if __name__ == "__main__":
    app()

