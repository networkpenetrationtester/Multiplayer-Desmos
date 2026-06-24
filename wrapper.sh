#! /bin/bash
# TODO: venv
# TODO: install requirements
# TODO:

src="./config/internal.env"
acl="./config/redis.acl"

set -a
source $src

echo "# AUTOMATICALLY GENERATED FROM $src" >$acl
echo "user default off" >>$acl
echo "user $REDIS_USERNAME on >$REDIS_PASSWORD ~* +@all" >>$acl

docker compose --profile $1 $2 --build || echo "======== USAGE: bash wrapper.sh <profile> <up|down|etc...> ========"
