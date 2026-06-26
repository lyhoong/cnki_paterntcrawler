# 知网文献爬虫项目

## 项目简介

本项目使用 Python 的 Selenium 库爬取中国知网（CNKI）中的文献/专利数据，包括期刊论文、硕士论文、博士论文。可提取标题、摘要、关键词、公开时间等信息，并保存为 JSON 格式，并提供了json转换为MD文件方法。

## 功能特性

- 支持期刊论文（CFLS/CJFQ）、硕士论文（CMFD）、博士论文（CDFD）
- 每10篇文章实时保存一次 JSON 文件
- 每个 JSON 文件最多保存 3000 篇文章，超出自动分文件
- 支持断点续爬，程序中断后可继续爬取
- 自动过滤空摘要的文章

## 项目结构

```
cnki_lr_crawler-master/
├── README.md                    # 项目说明文档
└── script/                      #论文爬取脚本目录
    ├── config.py               # 配置属性文件
    ├── driver.py               # WebDriver初始化模块
    ├── cleaner.py              # 摘要清洗模块
    ├── saver.py                # JSON文件保存模块
    ├── spider_journal.py       # 期刊论文爬取脚本
    ├── spider_thesis.py        # 硕博论文爬取脚本
    ├── spider_main.py          # 主程序（根据配置调用对应爬虫）
    ├── process                # 工具模块
        ├── clean_json.py           # 清理JSON空摘要脚本
        ├── csv_to_json.py          # CSV文件转换为JSON文件(csv中的标题、摘要、关键词、时间)-参考output文件
        └── process_json.py         # JSON格式整理脚本(清理空摘要和补充key值)
        └── postprocess_to_md.py    # JSON内容提取为markdown文件(json/csv内容转换为markdown文件,并按照内存切分MD文件)
└── patent_script/ 专利爬取脚本目录
    ├──  postprocess_to_md.py      # JSON内容提取为markdown文件(json内容转换为markdown文件)
    ├──  spider_patent.py          # 专利爬取脚本
    ├──  ouput                     #爬取结果目录

```



## 模块说明

### 1. config.py - 配置属性文件

| 配置项 | 说明 | 示例值 |
|--------|------|--------|
| SEARCH_KEY | 搜索关键词 | 镁合金 |
| DOC_TYPE | 论文类型 | CMFD/CDFD/CFLS |
| OUTPUT_DIR | 输出目录 | 硕士_output |
| MAX_PAGES | 最大爬取页数 | 999 |
| MAX_ARTICLES | 单文件最大文章数 | 3000 |
| MAX_SIZE_MB | 单文件最大MB | 2.56 |


### 2. spider_journal.py - 期刊论文爬取脚本
### 注意该过程需要首先人为的进行验证码登录，且确保当下的网络可以支持浏览知网
爬取流程：
1. 搜索页面加载
2. 关键词输入并搜索
3. 遍历列表页，点击标题进入详情页
4. 提取标题、摘要、关键词、公开时间
5. 每10篇保存一次JSON

### 3. spider_thesis.py - 硕博论文爬取脚本

爬取流程：
1. 搜索页面加载
2. 切换到硕博论文标签
3. 关键词输入并搜索
4. 遍历列表页（tr表格结构），点击标题进入详情页
5. 提取标题、摘要、关键词、公开时间
6. 每10篇保存一次JSON
7. 每篇文章后保存断点

### 4. spider_main.py - 主程序 爬取网址为：https://kns.cnki.net/kns8s/AdvSearch

根据 config.py 中的 DOC_TYPE 自动选择对应的爬虫：
- CFLS/CJFQ → spider_journal.py
- CDFD/CMFD → spider_thesis.py

### 程序正式爬取前需要进行用户密码登录 爬取的网址:https://www.patentstar.com.cn/Search/TableSearch
### 5. spider_patent.py - 专利爬取主程序

## 使用流程

### 1. 配置修改

编辑 `config.py` 文件：

```python
# 搜索关键词
SEARCH_KEY = "镁合金"

# 论文类型：CMFD(硕士)/CDFD(博士)/CFLS(期刊)
DOC_TYPE = "CMFD"

# 输出目录
OUTPUT_DIR = "硕士_output"

# 单文件最大文章数
MAX_ARTICLES = 3000
```

### 2.1运行爬虫
知网爬虫
```bash
cd script
python spider_main.py
```
### 2.2专利之星爬虫
```bash
cd patent_script
python spider_patent.py
```

### 3. 查看结果

爬取完成后在 output 目录生成 JSON 文件：
- `知网文献_CMFD_1.json` - 第1个文件
- `知网文献_CMFD_2.json` - 第2个文件
- `checkpoint_CMFD.json` - 断点文件（爬取完成后自动删除）

### 4. 数据清洗（如需要）
# 整理JSON格式
python process_json.py
```

## 爬虫爬取-JSON输出格式

```json
{
  "keyword": "镁合金",
  "doc_type": "CMFD",
  "total": 3000,
  "file_index": 1,
  "start_id": 1,
  "articles": [
    {
      "id": 1,
      "title": "xxx",
      "abstract": "xxx",
      "keywords": "xxx",
      "publish_date": "2024-01-01",
      "abstract_len": 100
    }
  ]
}
```

## 注意事项
1. 网络稳定：确保网络连接正常，知网访问稳定
2. 验证码：遇到验证码时手动处理
3. 合理设置：避免过于频繁的请求
4. 断点续爬：程序异常退出后可重新运行，从断点继续

## 依赖安装

```bash
pip install selenium pandas
```
需要安装对应浏览器的 WebDriver（Edge 或 Chrome）。
下载网址：
Edge_webDriver:https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH