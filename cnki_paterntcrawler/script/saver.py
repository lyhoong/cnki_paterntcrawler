"""
知网爬虫通用模块 - JSON文件保存
优化：增量追加模式，每10篇保存一次，每个文件最多3000篇
"""

import json
import os

# 全局变量
current_file_index = 1
current_file_articles = []
current_file_article_count = 0  # 当前文件已有文章数


def init_saver():
    """初始化保存器"""
    global current_file_index, current_file_articles, current_file_article_count
    current_file_index = 1
    current_file_articles = []
    current_file_article_count = 0


def save_json_every_10(
    new_articles,
    output_file,
    max_articles,
    max_size_mb,
    output_dir,
    keyword="",
    doc_type="",
):
    """每10篇保存一次，增量追加模式"""
    global current_file_index, current_file_articles, current_file_article_count

    # 累积新文章
    current_file_articles.extend(new_articles)

    # 每累积10篇就保存一次
    if len(current_file_articles) >= 10:
        # 检查是否超过max_articles(3000篇)需要分新文件
        if current_file_article_count >= max_articles:
            print(f"文件{current_file_index}已保存 ({current_file_article_count}篇)")
            current_file_index += 1
            current_file_article_count = 0

        # 追加保存到当前文件
        _append_to_json(
            current_file_articles,
            current_file_index,
            output_file,
            max_size_mb,
            output_dir,
            keyword,
            doc_type,
        )

        print(
            f"已保存到: 知网文献_{doc_type}_{current_file_index}.json (累计{current_file_article_count + len(current_file_articles)}篇)"
        )

        current_file_article_count += len(current_file_articles)
        current_file_articles = []


def _append_to_json(
    articles,
    file_index,
    output_file,
    max_size_mb,
    output_dir,
    keyword="",
    doc_type="",
):
    """增量追加文章到JSON文件（不再读取整个文件合并）"""
    name, ext = os.path.splitext(output_file)
    filename = f"{name}_{file_index}{ext}"
    filepath = os.path.join(output_dir, filename)

    # 检查文件是否存在
    if os.path.exists(filepath):
        # 文件存在：读取现有articles数组，追加新文章
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                existing_articles = data.get("articles", [])
                # 保留keyword和doc_type
                existing_keyword = data.get("keyword", keyword)
                existing_doc_type = data.get("doc_type", doc_type)
        except:
            existing_articles = []
            existing_keyword = keyword
            existing_doc_type = doc_type
    else:
        # 文件不存在：创建新文件
        existing_articles = []
        existing_keyword = keyword
        existing_doc_type = doc_type

    # 将新文章（可能是元组）转换为字典列表
    new_articles_dict = []
    start_id = len(existing_articles) + 1
    for idx, item in enumerate(articles, start_id):
        if isinstance(item, (list, tuple)) and len(item) >= 5:
            new_articles_dict.append(
                {
                    "id": idx,
                    "title": item[0],
                    "abstract": item[1],
                    "keywords": item[2],
                    "publish_date": item[3],
                    "abstract_len": item[4],
                }
            )
        elif isinstance(item, dict):
            item["id"] = idx
            new_articles_dict.append(item)

    # 合并新旧文章
    all_articles = existing_articles + new_articles_dict

    data = {
        "keyword": existing_keyword,
        "doc_type": existing_doc_type,
        "total": len(all_articles),
        "file_index": file_index,
        "start_id": 1,
        "articles": all_articles,
    }

    # 直接写入完整文件
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_remaining(output_file, max_size_mb, output_dir, keyword="", doc_type=""):
    """保存剩余累积的文章"""
    global current_file_index, current_file_articles, current_file_article_count

    if current_file_articles:
        # 检查是否需要分新文件
        if current_file_article_count >= max_articles:
            print(f"文件{current_file_index}已保存 ({current_file_article_count}篇)")
            current_file_index += 1
            current_file_article_count = 0

        _append_to_json(
            current_file_articles,
            current_file_index,
            output_file,
            max_size_mb,
            output_dir,
            keyword,
            doc_type,
        )
        print(f"剩余文章已保存 ({len(current_file_articles)}篇)")
        current_file_article_count += len(current_file_articles)
        current_file_articles = []


def get_current_file_index():
    """获取当前文件索引"""
    return current_file_index


def set_current_file_index(index):
    """设置当前文件索引"""
    global current_file_index
    current_file_index = index
