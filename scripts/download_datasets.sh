#!/usr/bin/env bash
# ==============================================================================
# SatQuery AI — Remote Sensing Dataset Acquisition Script (PS 26167)
# ==============================================================================
set -e

DATA_DIR="./data"
mkdir -p "$DATA_DIR/bigearthnet"
mkdir -p "$DATA_DIR/rsvqa"
mkdir -p "$DATA_DIR/cdvqa"

echo "=========================================================="
echo "SatQuery AI: Downloading Benchmark & Adaptation Datasets"
echo "=========================================================="

# 1. BigEarthNet.txt (Multimodal Sentinel-1 SAR + Sentinel-2 Optical)
echo "[1/3] Setting up BigEarthNet metadata..."
# Note: Full BigEarthNet is ~100GB+. For development/hackathons, download sample splits:
echo "Target directory: $DATA_DIR/bigearthnet"
echo "Reference: https://bigearth.net"

# 2. RSVQA (Remote Sensing Visual Question Answering)
echo "[2/3] Setting up RSVQA Low/High Resolution splits..."
echo "Target directory: $DATA_DIR/rsvqa"
echo "Reference: https://rsvqa.sylvainlobry.com"

# 3. CDVQA (Change Detection Visual Question Answering)
echo "[3/3] Setting up CDVQA bi-temporal pairs..."
echo "Target directory: $DATA_DIR/cdvqa"

echo "Dataset scaffolding complete. Run python scripts/generate_sample_data.py for offline demo data."
