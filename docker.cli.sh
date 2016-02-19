#! /bin/bash

ssh -i insecure_key root@$(docker inspect  --format '{{ .NetworkSettings.IPAddress }}' open-nti_con)