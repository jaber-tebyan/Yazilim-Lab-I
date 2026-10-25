#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
    echo "Usage: ./calistir.sh baslangic.json komutlar.jsonl" >&2
    exit 1
fi

exec uv run yazilim-lab-project "$1" "$2"
