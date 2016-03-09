#!/bin/bash

#Load params file with all variables
source open-nti.params

# Build container 
docker build -t $IMAGE_NAME .

# Run all tests in tests directory
python -m pytest -v

