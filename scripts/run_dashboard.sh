#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export TRI_EDGE_HOME="${TRI_EDGE_HOME:-$REPO_ROOT}"

cd "$REPO_ROOT"

echo "[Tri-Edge Rescue] Starting Streamlit dashboard..."
python3 -m streamlit run dashboard/app.py --server.address 0.0.0.0
