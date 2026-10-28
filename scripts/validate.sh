#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
research_python="${RESEARCH_PYTHON:-.venv/bin/python}"
"$research_python" -m unittest discover -s tests -v
"$research_python" -m privacy_lab.verify_evidence \
  --live evidence/live-attempt-02 \
  --fixture evidence/fixture-attempt-04 \
  --fanout evidence/fanout-attempt-01/fanout.json \
  --output evidence/verification.json
"$research_python" -m privacy_lab.verify_followup
