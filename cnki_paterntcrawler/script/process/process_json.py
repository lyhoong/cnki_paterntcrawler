"""
JSON文件后处理脚本
功能：
1. 补齐articles数组中没有键值对的元素
2. 去除abstract为空或为NA的元素
3. 重新更新total值
"""

import json
import os

#TODO-文件所在目录
OUTPUT_DIR = "../output"


def fix_article(article, article_id):
    """修复单个文章格式，补齐键值对"""
    # 如果已经是字典，直接返回
    if isinstance(article, dict):
        return article

    # 如果是列表或元组，转换为字典
    if isinstance(article, (list, tuple)):
        if len(article) >= 5:
            return {
                "id": article_id,
                "title": article[0] if len(article) > 0 else "",
                "abstract": article[1] if len(article) > 1 else "NA",
                "keywords": article[2] if len(article) > 2 else "NA",
                "publish_date": article[3] if len(article) > 3 else "NA",
                "abstract_len": article[4] if len(article) > 4 else 0,
            }
        elif len(article) == 1:
            return {
                "id": article_id,
                "title": str(article[0]),
                "abstract": "NA",
                "keywords": "NA",
                "publish_date": "NA",
                "abstract_len": 0,
            }

    # 如果是字符串，尝试解析
    if isinstance(article, str):
        return {
            "id": article_id,
            "title": article[:50] if len(article) > 50 else article,
            "abstract": "NA",
            "keywords": "NA",
            "publish_date": "NA",
            "abstract_len": 0,
        }

    # 无法识别，返回空字典
    return {
        "id": article_id,
        "title": "NA",
        "abstract": "NA",
        "keywords": "NA",
        "publish_date": "NA",
        "abstract_len": 0,
    }


def clean_abstract_value(abstract):
    """判断abstract是否为空或NA"""
    if abstract is None:
        return True
    if isinstance(abstract, str):
        abstract = abstract.strip()
        if abstract == "" or abstract.upper() == "NA":
            return True
    return False


def process_json_file(filepath):
    """处理单个JSON文件"""
    print(f"\n处理: {os.path.basename(filepath)}")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"  [错误] 读取文件失败: {e}")
        return 0

    if "articles" not in data:
        print(f"  [跳过] 没有articles字段")
        return 0

    original_count = len(data["articles"])
    print(f"  原始文章数: {original_count}")

    # 处理每篇文章
    fixed_articles = []
    for idx, article in enumerate(data["articles"]):
        fixed_article = fix_article(article, idx + 1)
        fixed_articles.append(fixed_article)

    # 去除abstract为空或NA的元素
    cleaned_articles = [
        a for a in fixed_articles if not clean_abstract_value(a.get("abstract", "NA"))
    ]

    # 重新设置id
    for idx, article in enumerate(cleaned_articles):
        article["id"] = idx + 1

    removed_count = original_count - len(cleaned_articles)
    print(f"  去除空摘要: {removed_count}篇")
    print(f"  处理后文章数: {len(cleaned_articles)}")

    # 更新数据
    data["articles"] = cleaned_articles
    data["total"] = len(cleaned_articles)
    data["start_id"] = 1

    # 保存
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  [完成] 已保存")
    return removed_count


def main():
    """批量处理output目录下所有JSON文件"""
    print("=" * 50)
    print("JSON文件后处理")
    print("=" * 50)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 获取所有json文件
    json_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".json")]

    if not json_files:
        print("未找到JSON文件")
        return

    print(f"找到 {len(json_files)} 个JSON文件\n")

    total_removed = 0
    for filename in json_files:
        filepath = os.path.join(OUTPUT_DIR, filename)
        removed = process_json_file(filepath)
        total_removed += removed

    print(f"\n{'=' * 50}")
    print(f"处理完成! 共去除 {total_removed} 篇文章")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
