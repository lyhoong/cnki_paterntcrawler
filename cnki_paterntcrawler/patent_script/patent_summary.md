# 项目总结：专利数据 JSON → Markdown 后处理

## 目标

为 patentstar.com.cn 爬虫项目添加一个后处理程序，将 JSON 格式的专利数据转换为 Markdown 格式。规则：每个 JSON 中的 `articles` 数组元素，用 `title` 作为 Markdown 二级标题（`##`），`abstract` 作为标题下的内容。

## 实现要点

- **输入目录**：`output/`（与爬虫脚本 spider_patent.py 输出目录一致）
- **输出目录**：`markdown_output/`（脚本自动创建，不预先清空，只追加/覆盖同名文件）
- **文件对应**：每个 JSON 文件 → 同名 `.md` 文件（`patent_1.json` → `patent_1.md`）
- **扫描规则**：读取输入目录下 **所有** `.json` 文件（不限定文件名模式），按文件名排序
- **跳过规则**：`abstract` 为空/None/空白的数据条目不写入 Markdown
- **文件头部**：`# 专利数据 - 关键词：{keyword}` + `总条数：{total}`
- **编码**：UTF-8
- **文件覆盖**：同名 `.md` 文件会被覆盖写入（`open` 使用 `"w"` 模式）

## 过程发现

- 实际爬虫数据存放在 `专利_output/` 目录中（一个含中文目录名的目录），而爬虫脚本配置的输出目录为 `output/`；后续曾将数据从 `专利_output/` 复制到 `output/` 以验证转换脚本
- JSON 文件结构：`{"keyword": "镁合金", "total": 2527, "articles": [...]}`，每条 article 包含 `title`, `patent_number`, `publication_date`, `abstract`, `abstract_length`, `applicant`
- 中文编码为 UTF-8，但 Windows 终端（GBK）打印时可能出现编码错误，不影响文件写入
- 数据总量：patent_1.json 有 2527 条，patent_2.json 有 950 条，全部有 abstract（跳过数为0）

## 已完成

- [x] 创建 `postprocess_to_md.py` 脚本
- [x] 实现读取指定目录下所有 JSON 文件并按名排序
- [x] 实现将每篇文章的 title 作为 `##` 二级标题、abstract 作为正文
- [x] 实现 abstract 为空时跳过该条记录
- [x] 实现文件头部写入 keyword 和 total 元数据
- [x] 实现同名 `.md` 覆盖写入，但不清空目录中其他文件
- [x] 输入输出目录路径已简化：`output/` → `markdown_output/`

## 相关文件

- **后处理脚本**：`.\patent_script\postprocess_to_md.py`
- **爬虫脚本**：`.\patent_script\spider_patent.py`
- **JSON 输入目录**：`.\patent_script\output/`
- **Markdown 输出目录**：`.\patent_script\markdown_output/`
- **工作目录**：`.\patent_script/`
- 注意：爬虫真实数据在 `专利_output/` 目录中，如需测试后处理需先复制到 `output/`
