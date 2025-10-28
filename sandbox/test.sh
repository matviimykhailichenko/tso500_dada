#!/usr/bin/env bash
set -e

# --- Configuration ---
IMAGE="ichorcna:latest"
STAGING_DIR="$(pwd)/staging"
FILE_NAME="testfile.txt"

# --- Clean start ---
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR"

echo "[1] Creating file inside Docker as root (default user)"
docker run --rm -v "$STAGING_DIR":/data "$IMAGE" sh -c "echo 'Hello from Docker root!' > /data/$FILE_NAME"

echo "[2] File created, showing ownership:"
ls -l "$STAGING_DIR/$FILE_NAME" || true

echo "[3] Trying to delete file as host user..."
if rm "$STAGING_DIR/$FILE_NAME"; then
    echo "✅ Deleted successfully"
else
    echo "❌ Could not delete (owned by root)"
fi

echo "[4] Now creating the file with --user $(id -u):$(id -g)"
docker run --rm -v "$STAGING_DIR":/data --user $(id -u):$(id -g) "$IMAGE" \
    sh -c "echo 'Hello from Docker as $(id -u)' > /data/$FILE_NAME"

echo "[5] File created again, showing ownership:"
ls -l "$STAGING_DIR/$FILE_NAME"

echo "[6] Trying to delete it again..."
if rm "$STAGING_DIR/$FILE_NAME"; then
    echo "✅ Deleted successfully (correct UID/GID)"
else
    echo "❌ Could not delete"
fi
