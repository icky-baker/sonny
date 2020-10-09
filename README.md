# Distributed Systems - DFS project

![master](https://github.com/icky-baker/sonny/workflows/Linting/badge.svg?


## Team
### Danil Usmanov
### Egor Osokin
### Olya Chernukhina

## Group
BS-18-SB-01

## Date
### October 2020, semester 5

Table of Contents
=================

   * [Distributed Systems - DFS project](#distributed-systems---dfs-project)
   * [Table of contents](#table-of-contents)
   * [System launch](#system-launch)
   * [Architectural diagram](#architectural-diagram)
   * [Communication protocols](#communication-protocols)
      * [Endpoints](#endpoints)
         * [Naming Server](#naming-server)
         * [Storage Server](#storage-server)
      * [Communication Scenarios](#communication-scenarios)
      * [Background processes](#background-processes)
   * [Team](#team)
# System launch

**Prerequisites:**
1) 2 VPS instances with Ubuntu 18.04 or higher

**Installation guide in case of Docker is not preinstalled**
*If you have Docker go a step down*

1) Follow this [instruction](https://github.com/Birdi7/docker-install-ansible#how-to-use)
    ###### It will install Docker&Docker compose on your VPS via Ansible

**Installation guide in case of Docker is preinstalled**
1) Connect VPSs to swarm
    1. On VPC1: `docker swarm init`
    2. On VPC2: `docker swarm join --token $YOUR_TOKEN_HERE $YOUR_IP_HERE:2377`
3) Launch the project
    1) Clone this repository`git clone https://github.com/icky-baker/sonny.git`
    2) Go to the project folder `cd sonny`
    3) Launch `make deploy`

As a result, for example, our system looks like this:

![](https://i.imgur.com/HmgcELG.png)




# Architectural diagram

![](https://i.imgur.com/H71hx3N.png)

# Communication protocols

## Endpoints
*Note: All requests are listed in the format of [httpie](https://httpie.org)*

### Naming Server

#### for Client communication
* **`api/hosts/`**
    ###### Client request prototype
    `http GET "IP:PORT/api/hosts" Server-Hash:suchsecret`

    ###### Request details:
    1) Header
        * `Server-Hash` - value = *"suchsecret"*

* **`api/file/`**
    ###### Client request prototype
    1. `http GET "IP:PORT/api/file/?name=some_cool_name&cwd=/home/data/" Server-Hash:suchsecret`
    2. `http POST "IP:PORT/api/file/?name=bestfile&size=123&cwd=/home/data/" Server-Hash:suchsecret`

    ###### Request details:
    1) Parameters
        * `name` - name of the file
        * `cwd` - client's current working directory
        * `size` - size of  the file *(1 if creating a file)*
    2) Header
        * `Server-Hash` - value = *"suchsecret"*

* **`api/directory/`**
    ###### Client request prototype
    `http GET "IP:PORT/api/directory/?name=some_cool_name&cwd=/home/data/" Server-Hash:suchsecret`

    ###### Request details:
    1) Parameters
        * `name` - name of the directory
        * `cwd` - client's current working directory
    2) Header
        * `Server-Hash` - value = *"suchsecret"*

* **`api/init/`**
    ###### Client request prototype
    `http GET "IP:PORT/api/init/" Server-Hash:suchsecret`

    ###### Request details:
    1) Header
        * `Server-Hash` - value = *"suchsecret"*


#### for Storage Server communication

* **`api/server/register/`**
    ###### Server request prototype
    `http GET "IP:PORT/api/server/register/?space=345034&host=132.45.231.24&port=6541`

    ###### Request details:
    1) Parameters
        * `space` - available space on this server
        * `host` - storage server's ip
        * `port` - storage server's port

* **`api/server/approve/`**
    ###### Server request prototype
    `http GET "IP:PORT/api/server/approve/?space=345034&host=132.45.231.24&port=6541`

    ###### Request details:
    1) Parameters
        * `space` - available space on this server
        * `host` - storage server's ip
        * `port` - storage server's port

* **`api/file/approve/`**
    ###### Server request prototype
    `http POST "IP:PORT/api/file/approve/?name=some_cool_name&host=132.45.231.24&port=6541&cwd=/home/data/" file = filename,access_time=1558447897.0442736,modified_time=1558447897.04427334,change_time=435345.567567,size=234`

    ###### Request details:
    1) Parameters
        * `name` - name of the file
        * `cwd` - client's current working directory
        * `host` - storage server's ip
        * `port` - storage server's port
    2) Data
        * `file`
        * `access time`
        * `modified time`
        * `change time`
        * `size`
* **`api/file/delete/`**
    ###### Server request prototype
    `http POST "IP:PORT/api/file/approve/?name=some_cool_name&host=132.45.231.24&port=6541&cwd=/home/data/"`
    ###### Request details:
    1) Parameters
        * `name` - name of the file
        * `cwd` - client's current working directory
        * `host` - storage server's ip
        * `port` - storage server's port

### Storage Server

#### for Client communication
* **`api/dfs/`**
    ###### Client request prototype
    1. `http GET "IP:PORT/api/dfs/?command=file_copy&cwd=/home/data/&name=filename"`
    2. `http POST "IP:PORT/api/dfs/?command=file_write&cwd=/home/data/&name=filename" files = b'some_file_content'`

    ###### Request details:
    1) Parameters
        * `name` - name of the directory
        * `cwd` - client's current working directory
        * `command` - what command the client typed in
    2) Files *(for POST request only)*
        * `files` - content of the file we neet to upload to the server


#### for Naming Server communication
* **`api/`**
    ###### Server request prototype
    `http POST "IP:PORT/api/" files_to_replicate=[{some_file_content}{some_file_content}]`
    ###### Request details:
    1) Data
        * `files_to_replicate` - content of the files that are not still uploaded to the storage server


## Communication Scenarios


#### Initialize
*Initialize the client storage on a new system, should remove any existing file in the dfs root directory and return available size.*

* Client: `initialize`

![](https://i.imgur.com/sdsuJne.png)


#### File create
*Should allow to create a new empty file.*

* Client: `file-create [filename]`

![](https://i.imgur.com/KUibqjX.png)


#### File read
*Should allow to read any file from DFS (download a file from the DFS to the Client side).*
* Client: `file-read [filename]`

![](https://i.imgur.com/aiLBTnA.png)


#### File write
*Should allow to put any file to DFS (upload a file from the Client side to the DFS)*
* Client: `file-write [path_to_the_file]`

![](https://i.imgur.com/8QVfXZc.png)


#### File delete
*Should allow to delete any file from DFS*
* Client: `file-delete [filename]`

![](https://i.imgur.com/xfAvBJI.png)


#### File info
*Should provide information about the file (any useful information - size, node id, etc.)*
* Client: `file-info [filename]`

![](https://i.imgur.com/pHAjzu9.png)


#### File copy
*Should allow to create a copy of file.*
* Client: `file-copy [filename]`

![](https://i.imgur.com/AEmrAZo.png)


#### File move
*Should allow to move a file to the specified path.*
* Client: `file-move [filename] [destination_path]`

![](https://i.imgur.com/O47SBsm.png)


#### Open directory
*Should allow to change directory*
* Client: `open-directory [directory_name]` OR `ls`

![](https://i.imgur.com/FMjVftM.png)

#### Read directory
*Should return list of files, which are stored in the directory.*
* Client: `read-directory`

![](https://i.imgur.com/rh1AUHR.png)


#### Make directory
*Should allow to create a new directory.*
* Client: `make-directory [directory_name] [path: Optional]` or `mkdir [directory_name]`
If a `path` is provided, the directory `directory_name` is created in the `path`, otherwise, it is created in the current working direcory

![](https://i.imgur.com/gCdZlfJ.png)


#### Delete directory
*Should allow to delete directory.  If the directory contains files the system should ask for confirmation from the user before deletion.*
* Client: `delete-directory` OR `rmdir`

![](https://i.imgur.com/HR0GLOZ.png)

## Background processes

1) Naming Server checks the state of Storage Servers every n seconds via `http GET "api/"`
2) When Storage Server comes back to life, it initializes via `http GET api/server/register/` and receives the current system state
3) When Storage Server successfully updated everything and is ready to work, it sends `http GET api/server/approve/`
![](https://i.imgur.com/uQxdQEp.png)


# Team
Danil Usmanov - storage server, deployment

Egor Osokin - naming server, deployment

Olya Chernukhina - client, documentation
