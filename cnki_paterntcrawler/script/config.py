"""
知网爬虫配置属性文件
"""

# 搜索关键词
SEARCH_KEY = "镁合金"

# 爬取知网文章的类型
DOC_TYPE = "CMFD"  # 期刊(CJFQ/CFLS), 博士(CDFD), 硕士(CMFD)

# 根据DOC_TYPE生成输出文件名和断点文件名
OUTPUT_FILE = f"知网文献_{DOC_TYPE}.json"
CHECKPOINT_FILE = f"checkpoint_{DOC_TYPE}.json"

# 输出文件保存目录
OUTPUT_DIR = "output"

MAX_PAGES = 999  # 爬取页数（设置很大以爬取全部）

MAX_ARTICLES = 3000  # 每个json文件最多3000篇文章

MAX_SIZE_MB = 2.56  # 单个JSON文件最大MB，超过则保存到新文件
