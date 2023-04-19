#!/bin/bash

#docker \
podman \
  run \
  -p 5000:5000 \
  -v $PWD:/app:Z \
  pycacho
