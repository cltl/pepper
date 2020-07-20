#!/bin/sh

curl -X POST http://localhost:7200/rest/repositories -H 'Content-Type: multipart/form-data' -F 'config=@repo-config.ttl'
