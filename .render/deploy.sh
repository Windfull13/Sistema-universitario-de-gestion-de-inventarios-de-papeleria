#!/bin/bash
set -e
echo "=== Starting deployment ==="
echo "Current app.py:"
head -20 /opt/render/project/src/app.py
echo ""
echo "=== Running database cleanup ==="
python /opt/render/project/src/clear_db.py || true
echo "=== Deployment complete ==="
