import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#TODO-每次启动前会删除output下的内容

key_word = "镁合金"
url = "https://www.patentstar.com.cn/Search/TableSearch"

input_xpath = "/html/body/div[1]/div[2]/div[1]/div[1]/div[2]/div[4]/input"
search_xpath = "/html/body/div[1]/div[2]/div[1]/div[1]/div[2]/div[21]/button[1]"
page_15_xpath = "/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div/div/ul/li[3]/a"
next_page_xpath = "//a[@class='nextPage']"

title_xpath = (
    "/html/body/div[1]/div[2]/div/div[2]/div[4]/div[1]/div[1]/div/div[1]/label"
)
patent_number_xpath = "/html/body/div[1]/div[2]/div/div[2]/div[4]/div[1]/div[1]/div/div[2]/div[2]/div[1]/p[3]/span"
publication_date_xpath = "/html/body/div[1]/div[2]/div/div[2]/div[4]/div[1]/div[2]/div/div[2]/div[2]/div[1]/p[4]/span"
abstract_xpath = "/html/body/div[1]/div[2]/div/div[2]/div[4]/div[1]/div[1]/div/div[2]/div[2]/div[4]/p/span"
applicant_xpath = "/html/body/div[1]/div[2]/div/div[2]/div[4]/div[1]/div[1]/div/div[2]/div[2]/div[3]/p[1]/a/span"

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
max_file_size = 2.56 * 1024 * 1024


def init_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Edge(options=options)
    driver.get(url)
    return driver


def wait_for_login(driver):
    print("请在浏览器中完成登录...")
    input("登录完成后，请按回车键继续...")
    print("继续执行...")


def search_keyword(driver, keyword):
    wait = WebDriverWait(driver, 30)
    input_elem = wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))
    time.sleep(3)
    input_elem.clear()
    input_elem.send_keys(keyword)
    time.sleep(2)

    search_btn = wait.until(EC.presence_of_element_located((By.XPATH, search_xpath)))
    driver.execute_script("arguments[0].click();", search_btn)

    print("等待搜索结果加载（可能需要较长时间）...")
    time.sleep(25)

    try:
        result_xpath = "/html/body/div[1]/div[2]/div/div[2]/div[4]/div[1]/div[1]"
        wait.until(EC.presence_of_element_located((By.XPATH, result_xpath)))
        print("搜索结果已加载")
    except:
        print("等待结果加载超时，继续尝试...")


def set_page_size(driver):
    try:
        time.sleep(3)
        ul_xpath = "/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div/div/ul"
        li_15_xpath = f"{ul_xpath}/li[@data-value='15']"

        wait = WebDriverWait(driver, 30)
        li_15 = wait.until(EC.presence_of_element_located((By.XPATH, li_15_xpath)))

        if "filter-selected" in li_15.get_attribute("class"):
            print("当前已设置为每页15条")
            return

        driver.execute_script("arguments[0].click();", li_15)

        print("等待15条数据加载（可能需要较长时间）...")
        time.sleep(25)

        try:
            result_xpath = "/html/body/div[1]/div[2]/div/div[2]/div[4]/div[1]/div[1]"
            wait.until(EC.presence_of_element_located((By.XPATH, result_xpath)))
            print("15条数据已加载")
        except:
            print("等待数据加载超时，继续尝试...")

    except Exception as e:
        print(f"设置每页15条失败: {e}")


def extract_single_patent(driver, index):
    try:
        base1_xpath = (
            f"/html/body/div[1]/div[2]/div/div[2]/div[4]/div[1]/div[{index}]/div"
        )
        base2_xpath = f"/html/body/div[1]/div[2]/div/div[2]/div[4]/div[1]/div[{index}]/div/div[2]/div[2]"

        try:
            title_elem = driver.find_element(By.XPATH, f"{base1_xpath}/div[1]/label")
            title = title_elem.text.strip() if title_elem else ""
        except:
            title = ""

        try:
            patent_num_elem = driver.find_element(
                By.XPATH, f"{base2_xpath}/div[1]/p[3]/span"
            )
            patent_number = patent_num_elem.text.strip() if patent_num_elem else ""
        except:
            patent_number = ""

        try:
            pub_date_elem = driver.find_element(
                By.XPATH, f"{base2_xpath}/div[1]/p[4]/span"
            )
            publication_date = pub_date_elem.text.strip() if pub_date_elem else ""
        except:
            publication_date = ""

        try:
            abstract_elem = driver.find_element(
                By.XPATH, f"{base2_xpath}/div[4]/p/span"
            )
            abstract = abstract_elem.text.strip() if abstract_elem else ""
        except:
            abstract = ""

        try:
            applicant_elem = driver.find_element(
                By.XPATH, f"{base2_xpath}/div[3]/p[1]/a/span"
            )
            applicant = applicant_elem.text.strip() if applicant_elem else ""
        except:
            applicant = ""

        if not abstract:
            return None

        abstract_length = len(abstract) if abstract else 0

        return {
            "title": title,
            "patent_number": patent_number,
            "publication_date": publication_date,
            "abstract": abstract,
            "abstract_length": abstract_length,
            "applicant": applicant,
        }
    except Exception as e:
        print(f"提取第{index}条专利失败: {e}")
        return None


def extract_page_data(driver):
    patents = []
    for i in range(1, 16):
        patent = extract_single_patent(driver, i)
        if patent:
            patents.append(patent)
    return patents


def has_next_page(driver):
    try:
        next_btn = driver.find_element(By.XPATH, next_page_xpath)
        class_attr = next_btn.get_attribute("class") or ""

        print(f"下一页按钮class: {class_attr}")

        if "disabled" in class_attr:
            print("检测到disabled状态，没有下一页")
            return False
        return True
    except Exception as e:
        print(f"检查下一页失败: {e}")
        return False
        if not href or href == "javascript:void(0)":
            print("没有有效href，没有下一页")
            return False
        return True
    except Exception as e:
        print(f"检查下一页失败: {e}")
        return False


def click_next_page(driver):
    try:
        wait = WebDriverWait(driver, 30)
        next_btn = wait.until(
            EC.presence_of_element_located((By.XPATH, next_page_xpath))
        )
        driver.execute_script("arguments[0].click();", next_btn)

        print("等待下一页加载...")
        time.sleep(5)

        try:
            result_xpath = "/html/body/div[1]/div[2]/div/div[2]/div[4]/div[1]/div[1]"
            wait.until(EC.presence_of_element_located((By.XPATH, result_xpath)))
            print("下一页已加载")
        except:
            print("等待下一页加载超时，继续尝试...")

        return True
    except Exception as e:
        print(f"点击下一页失败: {e}")
        return False
        return False


def get_file_size(filepath):
    if os.path.exists(filepath):
        return os.path.getsize(filepath)
    return 0


def save_data(data, file_path, total_count):
    with open(file_path, "r", encoding="utf-8") as f:
        existing_data = json.load(f)
    existing_data["articles"].extend(data)
    existing_data["total"] = total_count
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)


def run():
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        for f in os.listdir(output_dir):
            if f.endswith(".json"):
                os.remove(os.path.join(output_dir, f))
        print("已清空旧的json文件")

    driver = init_driver()

    try:
        wait_for_login(driver)
        search_keyword(driver, key_word)
        set_page_size(driver)

        file_index = 1
        current_file = os.path.join(output_dir, f"patent_{file_index}.json")

        initial_data = {"keyword": key_word, "total": 0, "articles": []}
        with open(current_file, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=2)

        total_count = 0
        page_count = 0

        while True:
            page_count += 1
            print(f"正在抓取第 {page_count} 页...")

            time.sleep(9)

            patents = extract_page_data(driver)
            print(f"本页获取 {len(patents)} 条数据")

            if len(patents) == 0:
                print("未获取到数据，可能页面结构变化或加载失败")
                break

            current_size = get_file_size(current_file)
            data_json = json.dumps(patents, ensure_ascii=False)
            data_size = len(data_json.encode("utf-8"))

            if current_size + data_size > max_file_size:
                file_index += 1
                current_file = os.path.join(output_dir, f"patent_{file_index}.json")
                initial_data = {"keyword": key_word, "total": 0, "articles": []}
                with open(current_file, "w", encoding="utf-8") as f:
                    json.dump(initial_data, f, ensure_ascii=False, indent=2)
                print(f"新建文件: patent_{file_index}.json")

            total_count += len(patents)
            save_data(patents, current_file, total_count)
            print(f"累计抓取 {total_count} 条数据")

            time.sleep(2)

            has_next = has_next_page(driver)
            print(f"是否有下一页: {has_next}")

            if has_next:
                if not click_next_page(driver):
                    print("点击下一页失败，停止爬取")
                    break
            else:
                print("已到达最后一页")
                break

        for i in range(1, file_index + 1):
            file_path = os.path.join(output_dir, f"patent_{i}.json")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["total"] = total_count
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"抓取完成！共抓取 {total_count} 条数据，分布在 {file_index} 个文件中")

    except Exception as e:
        print(f"运行出错: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    # 专利之星的账号和密码
    # user:xxxx
    # password:xxxx
    run()
