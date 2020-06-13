#!/bin/sh


BIN_DIR=`dirname $0`
PROJECT_DIR="${BIN_DIR}/.."
export SERVER="${1}"
export SERVICE="${2}"

if [ -z "${SERVER}" ]; then
  echo "Usage: $0 <server> <service>" >&1
  exit 1
fi

if [ -z "${SERVICE}" ]; then
  echo "Usage: $0 <server> <service>" >&1
  exit 1
fi

. ${BIN_DIR}/common.sh

cd ${PROJECT_ROOT}
echo "Deploying code"
rsync \
  -avc \
  --progress \
  --delete-after \
  ./ \
  --exclude=*.pyc \
  --exclude=Makefile \
  --exclude=.git \
  --exclude=ansible \
  --exclude=build \
  --exclude=cbsd.conf \
  --exclude=dist \
  --exclude=*.egg-info \
  --exclude="*.mk" \
  --exclude="local_*" \
  ${SERVER}:repos/${SERVICE}/
