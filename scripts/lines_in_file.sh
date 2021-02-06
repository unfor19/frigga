#!/bin/bash
set -e
set -o pipefail

_FILE_PATH="${1:-$FILE_PATH}"
_FILE_PATH="${_FILE_PATH:-Dockerfile}"
_SHOW_CONTENTS="${2:-$SHOW_CONTENTS}"
_SHOW_CONTENTS="${_SHOW_CONTENTS:-false}"


if ! test -f "$_FILE_PATH" ; then
    echo "$_FILE_PATH not found"
    exit 1
fi

_FILE_CONTENTS=$(sed 's/^#.*$//;/^$/d' "$_FILE_PATH")
_FILE_LINES=$(echo "$_FILE_CONTENTS" | wc -l)

[[ "$_SHOW_CONTENTS" != "false" ]] && echo "$_FILE_CONTENTS"
echo "$_FILE_LINES"