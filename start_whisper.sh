#!/bin/bash
# Starts the Wyoming Whisper Server on Port 10300
# Usage: ./start_whisper.sh

DATA_DIR="$HOME/.local/share/tuxtalks/wyoming-data"
mkdir -p "$DATA_DIR"

echo "Starting Wyoming Whisper (Microservice)..."
echo "Host: localhost"
echo "Port: 10301"
echo "Device: CPU (INT8)"
echo "Data Dir: $DATA_DIR"
echo "-----------------------------------"
echo "Keep this window open while using TuxTalks with Whisper."

wyoming-faster-whisper \
    --uri tcp://127.0.0.1:10301 \
    --model tiny \
    --language en \
    --device cpu \
    --compute-type int8 \
    --beam-size 1 \
    --data-dir /home/startux/.local/share/tuxtalks/wyoming-data > /home/startux/code/tuxtalks/server.log 2>&1
