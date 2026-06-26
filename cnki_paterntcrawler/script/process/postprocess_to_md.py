import os
import json
import csv
import re

# 尝试导入 chardet 用于自动检测编码（可选）
try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False
#TODO 文件输入目录
INPUT_DIR = "../output"
# TODO 输出目录
OUTPUT_DIR = "../markdown_output"

MAX_MD_SIZE_BYTES = int(2.56 * 1024 * 1024)   # 2.56 MB

# ------------------------------------------------------------
# 通用辅助函数
# ------------------------------------------------------------
def detect_encoding(file_path):
    if HAS_CHARDET:
        with open(file_path, 'rb') as f:
            raw = f.read(10000)
            result = chardet.detect(raw)
            return result['encoding'] or 'utf-8'
    return 'utf-8-sig'

def detect_delimiter(file_path, encoding):
    with open(file_path, 'r', encoding=encoding) as f:
        first_line = f.readline()
    candidates = [',', ';', '\t', '|']
    counts = {d: first_line.count(d) for d in candidates}
    max_delim = max(counts, key=counts.get)
    return max_delim if counts[max_delim] > 0 else ','

def escape_markdown(text):
    escape_chars = r'([#*_\\`])'
    return re.sub(escape_chars, r'\\\1', text)

#去除首词为 Abstract
def clean_abstract(abstract):
    if not abstract:
        return abstract
    return re.sub(r'^Abstract\s*', '', abstract, flags=re.IGNORECASE)

def write_md_file(output_dir, base_filename, part_num, md_lines, part_article_count, keyword):
    """
    写入单个 Markdown 文件。
    part_num=0 表示无拆分，使用 base_filename；否则生成 base_partN.md
    返回生成的文件名
    """
    if part_num == 0:
        md_filename = base_filename
    else:
        name, ext = os.path.splitext(base_filename)
        md_filename = f"{name}_part{part_num}{ext}"
    md_path = os.path.join(output_dir, md_filename)

    # 修正总条数显示为该文件实际包含的文章数
    if part_article_count is not None:
        md_lines[1] = f"总条数：{part_article_count}"

    content = "\n".join(md_lines)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)

    size_mb = len(content.encode('utf-8')) / (1024 * 1024)
    print(f"  生成: {md_filename} (包含{part_article_count}篇, 大小{size_mb:.2f}MB)")
    return md_filename

# ------------------------------------------------------------
# JSON 转换
# ------------------------------------------------------------
def convert_json_to_md(json_path, output_dir):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    keyword = data.get("keyword", "")
    articles = data.get("articles", [])

    base_filename = os.path.basename(json_path).replace(".json", ".md")

    # 收集有效文章（有摘要的）
    valid_articles = []
    for art in articles:
        title = (art.get("title") or "").strip()
        abstract = (art.get("abstract") or "").strip()
        if not abstract:
            continue
        abstract = clean_abstract(abstract)
        title = escape_markdown(title)
        abstract = escape_markdown(abstract)
        valid_articles.append((title, abstract))

    if not valid_articles:
        print(f"警告: {json_path} 没有有效文章，跳过")
        return []

    # 文件头（占位总条数）
    header = [
        f"# sci数据 - 关键词：{keyword}",
        "总条数：0",
        "",
    ]
    header_content = "\n".join(header)
    header_bytes = len(header_content.encode('utf-8'))

    generated_files = []
    current_md_lines = header.copy()
    current_bytes = header_bytes
    current_articles = []
    part_num = 0

    for title, abstract in valid_articles:
        article_lines = [f"## {title}", "", abstract, ""]
        article_content = "\n".join(article_lines)
        article_bytes = len(article_content.encode('utf-8'))

        # 拆分条件：加入后超限 且 当前已有至少一篇文章
        if current_bytes + article_bytes > MAX_MD_SIZE_BYTES and current_articles:
            part_num += 1
            write_md_file(output_dir, base_filename, part_num,
                          current_md_lines, len(current_articles), keyword)
            # 重置
            current_md_lines = header.copy()
            current_bytes = header_bytes
            current_articles = []

        current_md_lines.extend(article_lines)
        current_bytes += article_bytes
        current_articles.append((title, abstract))

    # 写入最后一部分
    if current_articles:
        part_num += 1
        write_md_file(output_dir, base_filename, part_num,
                      current_md_lines, len(current_articles), keyword)

    # 单文件时去除 _part1 后缀
    if part_num == 1 and generated_files:
        old_name = generated_files[0]
        new_name = base_filename
        os.rename(os.path.join(output_dir, old_name), os.path.join(output_dir, new_name))
        generated_files[0] = new_name
        print(f"  重命名为: {new_name}")

    return generated_files

# ------------------------------------------------------------
# CSV 转换
# ------------------------------------------------------------
def convert_csv_to_md(csv_path, output_dir):
    encoding = detect_encoding(csv_path)
    delimiter = detect_delimiter(csv_path, encoding)

    records = []
    keyword_from_file = None

    with open(csv_path, 'r', encoding=encoding) as f:
        reader = csv.reader(f, delimiter=delimiter)
        try:
            header = next(reader)
        except StopIteration:
            print(f"警告：{csv_path} 为空，跳过")
            return []

        header = [h.strip().lower() for h in header]
        try:
            title_idx = header.index("title")
            abstract_idx = header.index("abstract")
        except ValueError:
            print(f"错误：{csv_path} 缺少 title 或 abstract 列，跳过")
            return []

        keyword_idx = header.index("keyword") if "keyword" in header else None

        for row in reader:
            if len(row) <= max(title_idx, abstract_idx):
                continue
            title = row[title_idx].strip() if title_idx < len(row) else ""
            abstract = row[abstract_idx].strip() if abstract_idx < len(row) else ""
            if not abstract:
                continue

            if keyword_idx is not None and keyword_idx < len(row):
                kw = row[keyword_idx].strip()
                if kw:
                    keyword_from_file = kw

            records.append((title, abstract))

    if not records:
        print(f"警告：{csv_path} 没有有效文章，跳过")
        return []

    keyword = keyword_from_file if keyword_from_file else os.path.splitext(os.path.basename(csv_path))[0]
    base_filename = os.path.basename(csv_path).replace(".csv", ".md")

    header = [
        f"# sci数据 - 关键词：{keyword}",
        "总条数：0",
        "",
    ]
    header_content = "\n".join(header)
    header_bytes = len(header_content.encode('utf-8'))

    generated_files = []
    current_md_lines = header.copy()
    current_bytes = header_bytes
    current_articles = []
    part_num = 0

    for title, abstract in records:
        abstract = clean_abstract(abstract)
        title = escape_markdown(title)
        abstract = escape_markdown(abstract)

        article_lines = [f"## {title}", "", abstract, ""]
        article_content = "\n".join(article_lines)
        article_bytes = len(article_content.encode('utf-8'))

        if current_bytes + article_bytes > MAX_MD_SIZE_BYTES and current_articles:
            part_num += 1
            write_md_file(output_dir, base_filename, part_num,
                          current_md_lines, len(current_articles), keyword)
            current_md_lines = header.copy()
            current_bytes = header_bytes
            current_articles = []

        current_md_lines.extend(article_lines)
        current_bytes += article_bytes
        current_articles.append((title, abstract))

    if current_articles:
        part_num += 1
        write_md_file(output_dir, base_filename, part_num,
                      current_md_lines, len(current_articles), keyword)

    if part_num == 1 and generated_files:
        old_name = generated_files[0]
        new_name = base_filename
        os.rename(os.path.join(output_dir, old_name), os.path.join(output_dir, new_name))
        generated_files[0] = new_name
        print(f"  重命名为: {new_name}")

    return generated_files

# ------------------------------------------------------------
# 主流程
# ------------------------------------------------------------
def get_sorted_files(directory, extension):
    files = [f for f in os.listdir(directory) if f.endswith(extension)]
    files.sort()
    return files
#转换文件
def convert():
    if not os.path.exists(INPUT_DIR):
        print(f"输入目录不存在: {INPUT_DIR}")
        return

    json_files = get_sorted_files(INPUT_DIR, ".json")
    csv_files = get_sorted_files(INPUT_DIR, ".csv")

    if not json_files and not csv_files:
        print(f"在 {INPUT_DIR} 下未找到 .json 或 .csv 文件")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for f in os.listdir(OUTPUT_DIR):
        if f.endswith(".md"):
            os.remove(os.path.join(OUTPUT_DIR, f))

    for json_file in json_files:
        print(f"处理 JSON: {json_file}")
        json_path = os.path.join(INPUT_DIR, json_file)
        files = convert_json_to_md(json_path, OUTPUT_DIR)
        print(f"  生成 {len(files)} 个 Markdown 文件\n")

    for csv_file in csv_files:
        print(f"处理 CSV: {csv_file}")
        csv_path = os.path.join(INPUT_DIR, csv_file)
        files = convert_csv_to_md(csv_path, OUTPUT_DIR)
        print(f"  生成 {len(files)} 个 Markdown 文件\n")

    print(f"\n转换完成！输出目录: {OUTPUT_DIR}")

if __name__ == "__main__":
    convert()