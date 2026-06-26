import json
import os
import re

# 配置目录
OUTPUT_DIR = "../output"

# 正则：匹配开头 Abstract / abstract / ABSTRACT 后跟任意分隔符（空格、冒号、点）
abstract_prefix_pattern = re.compile(r'^Abstract[:.\s]*', re.IGNORECASE)

"""
清理单个JSON文件：
1. 移除abstract为空/NA的文章
2. 清除摘要开头的Abstract关键词（含冒号、空格）
"""
def clean_json_file(input_file, output_file=None):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    original_count = len(data["articles"])
    cleaned_articles = []
    for article in data["articles"]:
        abstract = article.get("abstract", "")
        # 清洗：去掉开头Abstract标识
        clean_abs = abstract_prefix_pattern.sub("", abstract).strip()
        article["abstract"] = clean_abs
        # 过滤空摘要
        if clean_abs not in ("NA", "") and clean_abs:
            cleaned_articles.append(article)

    data["articles"] = cleaned_articles
    data["total"] = len(cleaned_articles)

    output_file = output_file or input_file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    removed = original_count - len(cleaned_articles)
    print(
        f"{input_file}: {original_count}篇 -> {len(cleaned_articles)}篇 (移除:{removed})"
    )
    return removed


def main():
    """批量清理output目录下所有JSON文件"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    json_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".json")]

    if not json_files:
        print("未找到JSON文件")
        return

    print(f"找到 {len(json_files)} 个JSON文件\n")

    total_removed = 0
    for filename in json_files:
        input_path = os.path.join(OUTPUT_DIR, filename)
        removed = clean_json_file(input_path)
        total_removed += removed

    print(f"\n完成! 共移除 {total_removed} 篇文章")

if __name__ == "__main__":
    main()