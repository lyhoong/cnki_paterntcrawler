"""
知网爬虫通用模块 - 清洗摘要和关键词
"""

import re


def clean_abstract(text):
    """清洗摘要，只保留摘要和关键词部分"""
    if not text or text == "NA":
        return "NA", "NA"

    abstract = "NA"
    keywords = "NA"

    try:
        # 提取关键词
        kw_pos = -1
        for match in re.finditer(r"关键词[：:]\s*", text, re.IGNORECASE):
            kw_pos = match.end()

        if kw_pos > 0:
            kw_text = text[kw_pos : kw_pos + 200]
            kw_end = len(kw_text)
            for char in ["\n", " ", "①", "②", "③", "1.", "2.", "•", "·"]:
                pos = kw_text.find(char)
                if pos > 0 and pos < kw_end:
                    kw_end = pos
            keywords = kw_text[:kw_end].strip()
            keywords = re.sub(r"\s*[;,，；]\s*", ", ", keywords)
            keywords = re.sub(r"^\s*[关键词：:\s]+", "", keywords, flags=re.IGNORECASE)
            keywords = keywords.strip()
            if len(keywords) < 2:
                keywords = "NA"

        # 提取摘要
        abs_pos_start = -1
        for match in re.finditer(r"摘要[：:]\s*", text, re.IGNORECASE):
            abs_pos_start = match.start()

        if abs_pos_start > 0:
            abs_start = abs_pos_start + len(
                re.search(r"摘要[：:]\s*", text, re.IGNORECASE).group()
            )

            abs_end = len(text)
            if keywords != "NA":
                kw_start_in_text = text.find("关键词：")
                if kw_start_in_text > abs_pos_start:
                    abs_end = kw_start_in_text
            else:
                for match in re.finditer(r"关键词[：:]\s*", text, re.IGNORECASE):
                    if match.start() > abs_pos_start:
                        abs_end = match.start()
                        break

            abstract = text[abs_start:abs_end].strip()

            # 清理摘要
            for pattern in [
                r"关键词[：:][^\n]+",
                r"基金[^\n]+",
                r"DOI[^\n]+",
                r"专辑[^\n]+",
                r"专题[^\n]+",
                r"分类号[^\n]+",
                r"在线公开时间[^\n]+",
                r"CNKI[^\n]+",
                r"^\s*[\s\n]+",
                r"^[Pasted.*]\s*",
            ]:
                abstract = re.sub(pattern, "", abstract, flags=re.IGNORECASE)

            abstract = abstract.strip()

            if len(abstract) < 30 or abstract.count("\n") > 10:
                abstract = "NA"

    except Exception as e:
        pass

    if not keywords or len(keywords) < 2:
        keywords = "NA"
    if not abstract or len(abstract) < 30:
        abstract = "NA"

    return abstract, keywords
