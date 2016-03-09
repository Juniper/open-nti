#!/bin/bash

#Load params file with all variables
source open-nti.params

docker build -t $IMAGE_NAME .

python -m pytest -v
