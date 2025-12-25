from __future__ import annotations
from dataclasses import dataclass
from typing import List
import tiktoken

@dataclass
class Chunk:
    index: int
    text: str
    token_count: int

def chunk_text(text: str, model: str, max_tokens_per_chunk: int = 1200) -> List[Chunk]:
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text)

    chunks = []
    start = 0
    idx = 0

    while start < len(tokens):
        end = min(start + max_tokens_per_chunk, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(Chunk(index=idx, text=chunk_text, token_count=len(chunk_tokens)))
        idx += 1
        start = end

    return chunks
