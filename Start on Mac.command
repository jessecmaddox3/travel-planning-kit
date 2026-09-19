#!/bin/sh
cd "$(dirname "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1 || ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)' >/dev/null 2>&1; then
  echo 'Install Python 3.11 or newer from https://www.python.org/downloads/ and try again.'
  echo 'Press Return to close.'
  read -r travel_answer
  exit 1
fi
python3 -m travel_kit start
travel_status=$?
if [ "$travel_status" -ne 0 ]; then
  echo 'The editor could not start. See docs/SETUP.md. Press Return to close.'
  read -r travel_answer
fi
exit "$travel_status"
