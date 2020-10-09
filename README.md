# sonny
DFS built for DS course
![master](https://github.com/actions/hello-world/workflows/Greet%20Everyone/badge.svg?branch=feature-1)

# Get started

1. Initialize environment with `make install`

# Requests to naming
Using [httpie](https://httpie.org)

## For storage servers
### Register server
`http "localhost:8000/api/server/register/?space=123&host=123.123.123.12&port=1234"`


## For client

### Hosts
`http GET "3.134.152.50:80/api/hosts" Server-Hash:suchsecret`

### Get file location
`http GET "3.134.152.50:80/api/file/?name=some cool name" Server-Hash:suchsecret`

### Allocate file
`http POST "3.134.152.50:80/api/file/?name=bestfile&size=123" Server-Hash:suchsecret`
