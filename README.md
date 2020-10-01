# sonny
DFS built for DS course

# Get started

1. Initialize environment with `make install`

# Requests to naming
Using [httpie](https://httpie.org)

## Register server
`http "localhost:8000/server/register/?space=123"`

If authetication is enabled, then `http "localhost:8000/server/register/?space=1234" Server-Hash:hash`

## Recover server
`http "localhost:8000/server/recover/?space=134"`

## Get file location
`http GET "localhost:8000/file/?name=some cool name&size=123&owner_hash=1170fb604e03d1a9a613"`

## Allocate file
`http POST "localhost:8000/file/allocate/?name=bestfile&size=123"`
