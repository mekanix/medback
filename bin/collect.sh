#!/bin/sh


BIN_DIR=`dirname $0`
PROJECT_DIR="${BIN_DIR}/.."
. ${BIN_DIR}/common.sh
setup

cd "${PROJECT_DIR}"
rm -rf static
flask collect --verbose
