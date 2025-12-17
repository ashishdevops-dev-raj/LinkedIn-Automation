import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1920,1080")

    # GitHub Actions runner already has chromedriver installed
    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)
    return driver


def login(driver, email, password):
    driver.get("https://www.linkedin.com/login")
    wait = WebDriverWait(driver, 15)

    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    try:
        wait.until(
            EC.any_of(
                EC.presence_of_element_located((By.ID, "global-nav-search")),
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'security')]")),
            )
        )
        print("Login attempted (CI-safe mode)")
    except Exception:
        print("LinkedIn blocked login on this runner (expected)")


def search_jobs(driver, keyword="DevOps Engineer", location="India"):
    driver.get("https://www.linkedin.com/jobs/search")
    wait = WebDriverWait(driver, 20)

    try:
        keyword_box = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[contains(@aria-label,'Search by title')]")
            )
        )
        keyword_box.clear()
        keyword_box.send_keys(keyword)

        location_box = driver.find_element(
            By.XPATH, "//input[contains(@aria-label,'City')]"
        )
        location_box.clear()
        location_box.send_keys(location)
        location_box.send_keys(Keys.RETURN)

        time.sleep(5)
    except TimeoutException:
        print("LinkedIn blocked automation or UI changed")


def easy_apply(driver, max_apply=5):
    wait = WebDriverWait(driver, 15)
    applied = 0

    buttons = driver.find_elements(
        By.XPATH, "//button[contains(@class,'jobs-apply-button')]"
    )

    for btn in buttons:
        if applied >= max_apply:
            break
        try:
            btn.click()
            time.sleep(2)

            submit = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button/span[text()='Submit application']")
                )
            )
            submit.click()
            applied += 1
            time.sleep(3)
        except Exception:
            continue

    return applied
