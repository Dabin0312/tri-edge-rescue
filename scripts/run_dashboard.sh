#!/bin/bash

cd ~/tri-edge-rescue

echo "[Tri-Edge Rescue] Starting Streamlit dashboard..."
python3 -m streamlit run dashboard/app.py --server.address 0.0.0.0
