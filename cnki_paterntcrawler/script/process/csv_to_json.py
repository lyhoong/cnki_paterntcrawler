import os
import json
import pandas as pd

# ===================== 配置区 =====================
CSV_INPUT_PATH = "../output/mg-sci-all.csv"
OUTPUT_DIR = "../output"
MAX_FILE_SIZE = int(2.56 * 1024 * 1024)  # 2.56MB 字节上限
GLOBAL_KEYWORD = "Mg alloy"
# CSV中出版年份、出版日期对应的列名，按需修改
COL_YEAR = "year"
COL_PUBLISH_DATE = "date"
# ==================================================

def is_blank(text) -> bool:
    """判断是否空/纯空白"""
    if pd.isna(text):
        return True
    s = str(text).strip()
    return len(s) == 0

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. pandas读取csv
    df = pd.read_csv(CSV_INPUT_PATH, dtype=str, encoding="utf-8")
    # 填充NaN为空字符串
    df = df.fillna("")

    # 2. 过滤：title和abstract都不为空的行
    df["title_blank"] = df["title"].apply(is_blank)
    df["abstract_blank"] = df["abstract"].apply(is_blank)
    valid_df = df[(~df["title_blank"]) & (~df["abstract_blank"])].copy()
    valid_total = len(valid_df)
    print(f"有效文献总数 total = {valid_total}")

    # 【核心修改】读取year、publish_date一并存入字典
    articles_all = valid_df[
        ["title", "abstract", "keywords", "doi", COL_YEAR, COL_PUBLISH_DATE]
    ].to_dict("records")

    file_index = 1
    current_chunk = []

    for item in articles_all:
        current_chunk.append(item)

        # 组装完整json结构，计算字节大小
        temp_data = {
            "keyword": GLOBAL_KEYWORD,
            "total": valid_total,
            "articles": current_chunk
        }
        temp_bytes = json.dumps(temp_data, ensure_ascii=False, indent=2).encode("utf-8")

        if len(temp_bytes) > MAX_FILE_SIZE:
            # 弹出最后一条，当前块写入文件
            last_item = current_chunk.pop()
            save_data = {
                "keyword": GLOBAL_KEYWORD,
                "total": valid_total,
                "articles": current_chunk
            }
            save_path = os.path.join(OUTPUT_DIR, f"output_{file_index}.json")
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            print(f"生成分片文件: {save_path}")
            file_index += 1
            current_chunk = [last_item]

    # 写入最后剩余数据块
    if current_chunk:
        final_data = {
            "keyword": GLOBAL_KEYWORD,
            "total": valid_total,
            "articles": current_chunk
        }
        save_path = os.path.join(OUTPUT_DIR, f"output_{file_index}.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        print(f"生成分片文件: {save_path}")

    print("转换完成！")

if __name__ == "__main__":
    main()