#!/usr/bin/env python3
"""Ingest a markdown file into ChromaDB with heading-based chunking."""

import os
import re
import sys

import chromadb


def chunk_markdown(text):
    """Split markdown text into chunks based on headings.

    Returns a list of dicts with keys: heading, level, content.
    """
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    chunks = []
    matches = list(heading_pattern.finditer(text))

    if not matches:
        # No headings — treat entire file as one chunk
        stripped = text.strip()
        if stripped:
            chunks.append({"heading": "Document", "level": 0, "content": stripped})
        return chunks

    # Text before the first heading
    preamble = text[: matches[0].start()].strip()
    if preamble:
        chunks.append({"heading": "Preamble", "level": 0, "content": preamble})

    for i, match in enumerate(matches):
        level = len(match.group(1))
        heading = match.group(2).strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        if content:
            chunks.append({"heading": heading, "level": level, "content": content})

    return chunks


def sanitize_collection_name(name):
    """Create a valid ChromaDB collection name from a filename."""
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    # Must start and end with alphanumeric
    name = name.strip("_-")
    if not name:
        name = "documents"
    # Must be 3-63 characters
    if len(name) < 3:
        name = name + "_collection"
    return name[:63]


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <markdown_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.isfile(filepath):
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        print("Error: File is empty.")
        sys.exit(1)

    chunks = chunk_markdown(text)
    if not chunks:
        print("Error: No content found to ingest.")
        sys.exit(1)

    basename = os.path.splitext(os.path.basename(filepath))[0]
    collection_name = sanitize_collection_name(basename)

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_data")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name=collection_name)

    documents = []
    metadatas = []
    ids = []

    for i, chunk in enumerate(chunks):
        documents.append(chunk["content"])
        metadatas.append({
            "source": os.path.basename(filepath),
            "heading": chunk["heading"],
            "heading_level": chunk["level"],
            "chunk_index": i,
        })
        ids.append(f"{basename}_chunk_{i}")

    collection.upsert(documents=documents, metadatas=metadatas, ids=ids)

    print(f"Ingested '{filepath}' into collection '{collection_name}'")
    print(f"  Chunks: {len(chunks)}")
    print(f"  DB path: {db_path}")
    print()
    for i, chunk in enumerate(chunks):
        preview = chunk["content"][:80].replace("\n", " ")
        print(f"  [{i}] {chunk['heading']} ({len(chunk['content'])} chars) — {preview}...")


if __name__ == "__main__":
    main()
