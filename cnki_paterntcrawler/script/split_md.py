import os
import sys
import math

MAX_BYTES = 2.56 * 1024 * 1024


def split_md(filepath: str):
    if not os.path.isfile(filepath):
        print(f"文件不存在: {filepath}")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    name, ext = os.path.splitext(filepath)
    out_dir = f"{name}_chunks"
    os.makedirs(out_dir, exist_ok=True)

    lines = content.splitlines(keepends=True)

    chunks = []
    current_lines = []

    for i, line in enumerate(lines):
        is_heading = line.startswith("## ")
        # If this line is a heading & current_chunk + next chunk would exceed limit, start new chunk
        if is_heading and current_lines:
            trial = len("".join(current_lines).encode("utf-8"))
            trial += len(line.encode("utf-8"))
            if trial >= MAX_BYTES:
                chunks.append(current_lines)
                current_lines = []
        current_lines.append(line)

        chunk_size = len("".join(current_lines).encode("utf-8"))
        if chunk_size >= MAX_BYTES:
            chunks.append(current_lines)
            current_lines = []

    if current_lines:
        chunks.append(current_lines)

    for idx, chunk_lines in enumerate(chunks, 1):
        out_path = f"{name}_part{idx}{ext}"
        with open(out_path, "w", encoding="utf-8") as f:
            f.writelines(chunk_lines)
        size_mb = len("".join(chunk_lines).encode("utf-8")) / (1024 * 1024)
        print(
            f" [{idx}/{len(chunks)}] {os.path.basename(out_path)} ({size_mb:.2f} MB)"
        )

    print(f"\n完成: {len(chunks)} 个文件 -> {out_dir}")


if __name__ == "__main__":
    split_md(filepath="./markdown_output/mg-sci-all.md")
