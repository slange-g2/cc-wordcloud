#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Generating word frequencies..."
python3 generate.py

echo "Starting server..."
python3 -m http.server 8000 &
SERVER_PID=$!

sleep 0.5
open http://localhost:8000

echo "Serving at http://localhost:8000 (PID $SERVER_PID)"
echo "Press Ctrl+C to stop."

trap "kill $SERVER_PID 2>/dev/null" EXIT
wait $SERVER_PID
