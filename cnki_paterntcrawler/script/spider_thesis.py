"""
知网硕博论文爬取脚本
"""

import os
import json
import re
import time

from selenium.webdriver.common.by import By

import config
from cleaner import clean_abstract
from driver import close_popup, init_driver as init_webdriver
from saver import init_saver, save_json_every_10, save_remaining

os.makedirs(config.OUTPUT_DIR, exist_ok=True)

CHECKPOINT_FILE = os.path.join(config.OUTPUT_DIR, config.CHECKPOINT_FILE)


def load_checkpoint():
    """加载断点"""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return (
                data.get("last_file_index", 1),
                data.get("last_article_count", 0),
                data.get("current_page", 1),
                data.get("current_article_index", 0),
            )
    return 1, 0, 1, 0


def save_checkpoint(file_index, article_count, current_page, current_article_index):
    """保存断点"""
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "keyword": config.SEARCH_KEY,
                "doc_type": config.DOC_TYPE,
                "last_file_index": file_index,
                "last_article_count": article_count,
                "current_page": current_page,
                "current_article_index": current_article_index,
            },
            f,
            ensure_ascii=False,
        )


def search_thesis(driver, keyword):
    """知网硕博论文搜索"""
    url = f"https://kns.cnki.net/kns8/AdvSearch?dbcode={config.DOC_TYPE}"
    driver.get(url)
    time.sleep(10)
    close_popup(driver)

    driver.find_element(
        By.XPATH, '//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[1]/a/span'
    ).click()
    time.sleep(1)

    inp = driver.find_element(By.XPATH, '//*[@id="gradetxt"]/dd[1]/div[2]/input')
    inp.clear()
    inp.send_keys(keyword)
    time.sleep(1)
    close_popup(driver)

    btn = driver.find_element(
        By.XPATH,
        "/html/body/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div/div[1]/div[2]/div[3]/div/input",
    )
    driver.execute_script("arguments[0].click();", btn)
    time.sleep(4)
    close_popup(driver)

    # 点击硕博论文标签
    try:
        driver.find_element(
            By.XPATH,
            "/html/body/div[2]/div[1]/div[2]/div/div/ul/li[2]/a",
        ).click()
        time.sleep(3)
        print("[OK] 已切换到硕博论文")

        # 重新输入关键词搜索
        inp = driver.find_element(By.XPATH, '//*[@id="gradetxt"]/dd[1]/div[2]/input')
        inp.clear()
        inp.send_keys(keyword)
        time.sleep(1)

        btn = driver.find_element(
            By.XPATH,
            "/html/body/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div/div[1]/div[2]/div[3]/div/input",
        )
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(5)
        close_popup(driver)
    except:
        pass

    time.sleep(2)

    # 设置每页50条
    try:
        driver.find_element(By.XPATH, '//*[@id="perPageDiv"]/div/i').click()
    except:
        try:
            driver.find_element(By.XPATH, '//*[@id="perPageNum"]/div/i').click()
        except:
            pass
    time.sleep(1)
    try:
        driver.find_element(By.XPATH, '//*[@id="perPageDiv"]/ul/li[3]/a').click()
    except:
        try:
            driver.find_element(By.XPATH, '//*[@id="perPageNum"]/ul/li[3]/a').click()
        except:
            pass
    time.sleep(3)


def get_detail_info(driver, title_elem):
    """点击标题进入详情页，获取完整信息"""
    title = title_elem.text.strip() if title_elem.text else "NA"
    abstract = "NA"
    keywords = "NA"
    publish_date = "NA"
    abstract_len = 0

    original = driver.current_window_handle
    new_window = None

    try:
        driver.execute_script("arguments[0].click();", title_elem)
        time.sleep(2)

        # 检查是否有新窗口
        for w in driver.window_handles:
            if w != original:
                new_window = w
                break

        if new_window:
            driver.switch_to.window(new_window)
            time.sleep(1.5)
        else:
            time.sleep(2)

        # 等待详情页加载
        for _ in range(10):
            page_text = driver.page_source
            if "摘要" in page_text and "detail" in page_text.lower():
                break
            time.sleep(0.5)

        # 尝试点击展开
        try:
            expand_links = driver.find_elements(
                By.XPATH,
                "//a[contains(text(),'展开') or contains(text(),'更多') or contains(text(),'查看完整摘要')]",
            )
            for link in expand_links:
                try:
                    if link.is_displayed():
                        driver.execute_script("arguments[0].click();", link)
                        time.sleep(1)
                        break
                except:
                    continue
        except:
            pass

        time.sleep(1)
        full_text = driver.execute_script("return document.body.innerText;")

        abstract, keywords = clean_abstract(full_text)

        if abstract != "NA":
            abstract_len = len(abstract)

        try:
            date_match = re.search(r"(\d{4}[-/年]\d{1,2}[-/月]\d{1,2})", full_text)
            if date_match:
                publish_date = date_match.group(1)
                publish_date = (
                    publish_date.replace("年", "-").replace("月", "-").replace("/", "-")
                )
        except:
            pass

        # 关闭详情页，返回列表
        if new_window:
            driver.close()
            driver.switch_to.window(original)
        else:
            driver.back()
        time.sleep(1)

    except Exception as e:
        # 确保返回列表页
        try:
            if new_window:
                for w in driver.window_handles:
                    if w != original:
                        try:
                            driver.switch_to.window(w)
                            driver.close()
                        except:
                            pass
                driver.switch_to.window(original)
            else:
                driver.back()
        except:
            pass
        time.sleep(1)

    return title, abstract, keywords, publish_date, abstract_len


def crawl_thesis(driver, max_pages):
    """爬取硕博数据"""
    last_file_index, last_count, last_page, last_article_index = load_checkpoint()
    print(
        f"断点: 文件{last_file_index}, 已爬{last_count}篇, 页{last_page}, 索引{last_article_index}"
    )

    articles = []
    count = 0
    file_index = last_file_index
    current_page = last_page
    current_article_index = last_article_index

    for page in range(1, max_pages + 1):
        if page < current_page:
            try:
                nb = driver.find_element(By.ID, "PageNext")
                if "disabled" in (nb.get_attribute("class") or "").lower():
                    break
                driver.execute_script("arguments[0].click();", nb)
                time.sleep(3)
            except:
                break
            continue

        print(f"\n--- 第{page}/{max_pages}页 ---")

        # 硕博论文使用tr
        try:
            items = driver.find_elements(By.XPATH, '//*[@id="gridTable"]//tr')
            cnt = len(items)
        except:
            cnt = 0
        print(f"条目数: {cnt}")

        if cnt == 0:
            try:
                nb = driver.find_element(By.ID, "PageNext")
                if "disabled" in (nb.get_attribute("class") or "").lower():
                    print("已到达最后一页")
                    break
            except:
                break
        time.sleep(2)

        for i in range(1, cnt + 1):
            if page == current_page and i <= current_article_index:
                continue

            if len(articles) >= config.MAX_ARTICLES:
                file_index += 1
                articles = []

            print(f"[{i}/{cnt}] ", end="", flush=True)

            # 硕博论文标题XPath
            title_xpath = f"/html/body/div[2]/div[2]/div[2]/div[2]/div/div[2]/div/div[1]/div/div/div/table/tbody/tr[{i}]/td[2]/div/a"
            try:
                title_elem = driver.find_element(By.XPATH, title_xpath)
            except:
                print("无标题")
                continue

            title, abstract, keywords, publish_date, abstract_len = get_detail_info(
                driver, title_elem
            )

            count += 1
            title_show = title[:20] + "..." if len(title) > 20 else title
            date_show = publish_date if publish_date != "NA" else "无"
            kw_show = (
                keywords[:15] + "..."
                if keywords != "NA" and len(keywords) > 15
                else keywords
            )
            print(
                f"{title_show} | {date_show} | 摘要:{abstract_len}字 | 关键词:{kw_show}"
            )

            if abstract != "NA" and abstract.strip():
                articles.append((title, abstract, keywords, publish_date, abstract_len))
            else:
                print(f"[跳过] 摘要为空")

            # 每篇文章后都保存断点
            save_checkpoint(file_index, count, page, i)

            if count % 10 == 0:
                print(f"\n  [每10篇保存] {count}篇...")
                save_json_every_10(
                    articles,
                    config.OUTPUT_FILE,
                    config.MAX_ARTICLES,
                    config.MAX_SIZE_MB,
                    config.OUTPUT_DIR,
                    config.SEARCH_KEY,
                    config.DOC_TYPE,
                )

        if page < max_pages:
            try:
                nb = driver.find_element(By.ID, "PageNext")
                if "disabled" in (nb.get_attribute("class") or "").lower():
                    print("已到达最后一页")
                    break
                driver.execute_script("arguments[0].click();", nb)
                time.sleep(3)
            except:
                break

    return count, page, i


def main():
    print("=" * 50)
    print("知网硕博论文爬虫")
    print(f"关键词: {config.SEARCH_KEY}")
    print(f"类型: {config.DOC_TYPE}")
    print("=" * 50)

    last_file, last_count, last_page, last_article_index = load_checkpoint()
    if last_count > 0:
        print(f"断点: 文件{last_file}, 已爬{last_count}篇, 页{last_page}")
    else:
        print("从头开始...")

    driver = init_webdriver()
    init_saver()

    try:
        print("\n[1] 搜索...")
        search_thesis(driver, config.SEARCH_KEY)

        print("\n[2] 爬取...")
        total_count, final_page, final_index = crawl_thesis(driver, config.MAX_PAGES)

        # 保存剩余文章
        save_remaining(
            config.OUTPUT_FILE,
            config.MAX_SIZE_MB,
            config.OUTPUT_DIR,
            config.SEARCH_KEY,
            config.DOC_TYPE,
        )

        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
        print(f"完成! 共爬取 {total_count} 篇")

    except KeyboardInterrupt:
        print("\n中断...")
        save_remaining(
            config.OUTPUT_FILE,
            config.MAX_SIZE_MB,
            config.OUTPUT_DIR,
            config.SEARCH_KEY,
            config.DOC_TYPE,
        )
        save_checkpoint(1, total_count, final_page, final_index)
    except Exception as e:
        print(f"\n错误: {e}")
        save_remaining(
            config.OUTPUT_FILE,
            config.MAX_SIZE_MB,
            config.OUTPUT_DIR,
            config.SEARCH_KEY,
            config.DOC_TYPE,
        )
        save_checkpoint(1, total_count, final_page, final_index)
    finally:
        try:
            driver.quit()
        except:
            pass


if __name__ == "__main__":
    main()
