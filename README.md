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
### Get file location
`http GET "localhost:8000/api/file/?name=some cool name"`

### Allocate file
`http POST "localhost:8000/api/file/allocate/?name=bestfile&size=123"`
