# sonny
DFS built for DS course

# Get started

1. Initialize environment with `make install`

# Requests to naming
Using [httpie](https://httpie.org)

## For storage servers
### Register server
`http "localhost:8000/api/server/register/?space=123"`

If authetication is enabled, then `http "localhost:8000/server/register/?space=1234" Server-Hash:hash`

### Recover server
`http "localhost:8000/api/server/recover/?space=134"`

## For client

### Hosts
`http GET "3.134.152.50:80/api/hosts" Server-Hash:suchsecret`

### Get file location
`http GET "3.134.152.50:80/api/file/?name=some cool name" Server-Hash:suchsecret`

### Allocate file
`http POST "3.134.152.50:80/api/file/allocate/?name=bestfile&size=123" Server-Hash:suchsecret`
