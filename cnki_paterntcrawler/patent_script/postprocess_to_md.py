import os
import json
import re

"""
 * 专利数据转换成Markdown
 *
 * 输入目录：output
 * 输出目录：markdown_output
"""
INPUT_DIR_PATH = "output"
OUTPUT_DIR_PATH = "markdown_output"

base_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(base_dir, INPUT_DIR_PATH)
output_dir = os.path.join(base_dir, OUTPUT_DIR_PATH)


def get_sorted_json_files(directory):
    files = [f for f in os.listdir(directory) if f.endswith(".json")]
    files.sort()
    return files


def convert():
    if not os.path.exists(input_dir):
        print(f"输入目录不存在: {input_dir}")
        print("请先运行 spider_patent.py 抓取数据")
        return

    json_files = get_sorted_json_files(input_dir)
    if not json_files:
        print(f"在 {input_dir} 下未找到 .json 文件")
        return

    os.makedirs(output_dir, exist_ok=True)

    for json_file in json_files:
        with open(os.path.join(input_dir, json_file), encoding="utf-8") as f:
            data = json.load(f)

        keyword = data.get("keyword", "")
        total = data.get("total", 0)
        articles = data.get("articles", [])

        md_lines = [
            f"# 专利数据 - 关键词：{keyword}",
            f"总条数：{total}",
            "",
        ]

        written_count = 0
        for article in articles:
            title = (article.get("title") or "").strip()
            abstract = (article.get("abstract") or "").strip()

            if not abstract:
                continue

            md_lines.append(f"## {title}")
            md_lines.append("")
            md_lines.append(abstract)
            md_lines.append("")
            written_count += 1

        md_filename = json_file.replace(".json", ".md")
        with open(os.path.join(output_dir, md_filename), "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        print(
            f"已生成: {md_filename} (共{len(articles)}条, 写入{written_count}条, "
            f"跳过{len(articles) - written_count}条)"
        )

    print(f"\n转换完成！输出目录: {output_dir}")


if __name__ == "__main__":
    convert()
