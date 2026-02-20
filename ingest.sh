#!/bin/bash
# Ingest a markdown file into ChromaDB

if [ -z "$1" ]; then
    echo "Usage: $0 <markdown_file>"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"
python "$SCRIPT_DIR/ingest_markdown.py" "$1"
