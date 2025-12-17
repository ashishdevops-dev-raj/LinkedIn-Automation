import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver


def login(driver, email, password):
    driver.get("https://www.linkedin.com/login")
    wait = WebDriverWait(driver, 15)

    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    time.sleep(5)


def search_jobs(driver, keyword="DevOps Engineer", location="India"):
    driver.get("https://www.linkedin.com/jobs")
    wait = WebDriverWait(driver, 15)

    search_box = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@aria-label,'Search jobs')]")))
    search_box.clear()
    search_box.send_keys(keyword)

    location_box = driver.find_element(By.XPATH, "//input[contains(@aria-label,'Search location')]" )
    location_box.clear()
    location_box.send_keys(location)
    location_box.send_keys(Keys.RETURN)

    time.sleep(5)


def easy_apply(driver, max_apply=5):
    wait = WebDriverWait(driver, 10)
    applied = 0

    jobs = driver.find_elements(By.XPATH, "//button[contains(@class,'jobs-apply-button')]")

    for job in jobs:
        if applied >= max_apply:
            break
        try:
            job.click()
            time.sleep(2)

            submit = wait.until(EC.element_to_be_clickable((By.XPATH, "//button/span[text()='Submit application']")))
            submit.click()
            applied += 1
            time.sleep(3)
        except Exception:
            continue

    return applied
