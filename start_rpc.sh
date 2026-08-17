#!/usr/bin/env bash
cd "$(dirname "$0")" || exit 1

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

python3 main.py >> rpc_output.log 2>&1
