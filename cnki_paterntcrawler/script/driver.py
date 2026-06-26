"""
知网爬虫通用模块 - Driver初始化
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By


def init_driver():
    """创建Edge WebDriver"""
    driver = webdriver.Edge()
    driver.set_page_load_timeout(60)
    print("[OK] Edge WebDriver")
    return driver


def init_chrome_driver():
    """创建Chrome WebDriver"""
    driver = webdriver.Chrome()
    driver.set_page_load_timeout(60)
    print("[OK] Chrome WebDriver")
    return driver


def close_popup(driver):
    """关闭推荐弹窗"""
    driver.execute_script("""
        document.querySelectorAll('.recommend-info-body,.dictlistX')
            .forEach(p => p.style.display = 'none');
    """)
    time.sleep(0.5)


def wait_page_load(driver, timeout=10):
    """等待页面加载完成"""
    driver.execute_script("document.readyState")
