# sonny
DFS built for DS course

# Get started

1. Initialize environment with `make install`

# Requests to naming
Using (httpie)[https://httpie.org]

## Register server
`http "localhost:8000/server/register/?space=123"`

## Recover server
`http "localhost:8000/server/recover/?space=134"`

## Allocate
`http "localhost:8000/file/allocate/?name=bestfile&size=1243"`
