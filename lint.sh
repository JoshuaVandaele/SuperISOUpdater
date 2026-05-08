#!/usr/bin/env bash
set -euo pipefail

python -m ruff check
python -m ruff format --check