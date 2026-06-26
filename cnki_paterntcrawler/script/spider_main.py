"""
知网爬虫主程序
根据config.py中的DOC_TYPE调用对应的爬虫脚本
"""
import importlib
import config

def main():
    print("=" * 50)
    print("知网文献爬虫主程序")
    print("=" * 50)
    print(f"关键词: {config.SEARCH_KEY}")
    print(f"类型: {config.DOC_TYPE}")
    print("=" * 50)

    doc_type = config.DOC_TYPE.upper()

    if doc_type in ("CFLS", "CJFQ"):
        print("\n[选择] 期刊论文爬虫")
        module_name = "spider_journal"
    elif doc_type in ("CDFD", "CMFD"):
        print("\n[选择] 硕博论文爬虫")
        module_name = "spider_thesis"
    else:
        print(f"\n[错误] 未知的DOC_TYPE: {doc_type}")
        print("可选: CFLS/CJFQ(期刊), CDFD(博士), CMFD(硕士)")
        return

    try:
        module = importlib.import_module(module_name)
        main_func = getattr(module, "main")
        main_func()
    except ImportError as e:
        print(f"\n[错误] 无法导入模块 {module_name}: {e}")
    except AttributeError as e:
        print(f"\n[错误] 模块 {module_name} 中没有main函数: {e}")
    except Exception as e:
        print(f"\n[错误] 运行失败: {e}")


if __name__ == "__main__":
    main()
