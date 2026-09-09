#!/usr/bin/env bash
# Start script for HuayuKaraoke web application
cd "$(dirname "$0")"

echo "=================================================="
echo "🎵 Starting HuayuKaraoke (华语K歌学堂)..."
echo "🌐 Open your browser at: http://localhost:8765"
echo "=================================================="

python3 app.py
