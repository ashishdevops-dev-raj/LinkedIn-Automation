from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time

def login(email, password):
    chrome_options = Options()
    # REMOVE --headless for local testing
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)

    driver.find_element(By.ID, "username").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    print(f"Logged in as {email}")
    time.sleep(5)
    return driver

def search_jobs(driver, keywords, location):
    all_job_links = []

    for keyword in keywords:
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword.replace(' ', '%20')}&location={location.replace(' ', '%20')}"
        driver.get(search_url)
        time.sleep(5)

        # Updated LinkedIn job card selector
        job_cards = driver.find_elements(By.CSS_SELECTOR, ".job-card-container--clickable")
        print(f"Found {len(job_cards)} job listings for '{keyword}'")

        for job in job_cards:
            try:
                link = job.find_element(By.TAG_NAME, "a").get_attribute("href")
                all_job_links.append(link)
            except NoSuchElementException:
                continue

    return all_job_links

def apply_jobs(driver, job_links, apply_limit=5):
    applied_count = 0
    wait = WebDriverWait(driver, 10)

    for link in job_links:
        if applied_count >= apply_limit:
            break

        try:
            driver.get(link)
            time.sleep(3)

            # Scroll to ensure page is loaded
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)

            # Try multiple selectors for Easy Apply button
            easy_apply = None
            selectors = [
                "button.jobs-apply-button",
                "button[data-control-name='jobdetails_topcard_inapply']",
                "button.jobs-s-apply__application-button",
                "//button[contains(@aria-label, 'Easy Apply')]",
                "//button[contains(text(), 'Easy Apply')]"
            ]

            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        easy_apply = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        easy_apply = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except (NoSuchElementException, TimeoutException):
                    continue

            if not easy_apply:
                print(f"Easy Apply not available for: {link}")
                continue

            # Click Easy Apply button
            try:
                driver.execute_script("arguments[0].click();", easy_apply)
                time.sleep(3)
            except ElementClickInterceptedException:
                print(f"Could not click Easy Apply button for: {link}")
                continue

            # Handle multi-step application process
            max_steps = 5
            step = 0
            
            while step < max_steps:
                step += 1
                time.sleep(2)
                
                # Check if there's a submit button
                submit_selectors = [
                    "button[aria-label='Submit application']",
                    "button[aria-label='Submit']",
                    "//button[contains(@aria-label, 'Submit')]",
                    "button.jobs-s-apply__application-button--submit"
                ]
                
                submit_btn = None
                for selector in submit_selectors:
                    try:
                        if selector.startswith("//"):
                            submit_btn = driver.find_element(By.XPATH, selector)
                        else:
                            submit_btn = driver.find_element(By.CSS_SELECTOR, selector)
                        if submit_btn.is_displayed() and submit_btn.is_enabled():
                            break
                    except NoSuchElementException:
                        continue

                if submit_btn:
                    try:
                        # Scroll to submit button
                        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", submit_btn)
                        print(f"✓ Applied to job: {link}")
                        applied_count += 1
                        time.sleep(3)
                        break
                    except Exception as e:
                        print(f"Error clicking submit button: {e}")
                        break

                # Check for "Next" button to continue multi-step form
                next_selectors = [
                    "button[aria-label='Continue to next step']",
                    "button[aria-label='Next']",
                    "//button[contains(@aria-label, 'Next')]",
                    "//button[contains(@aria-label, 'Continue')]"
                ]
                
                next_btn = None
                for selector in next_selectors:
                    try:
                        if selector.startswith("//"):
                            next_btn = driver.find_element(By.XPATH, selector)
                        else:
                            next_btn = driver.find_element(By.CSS_SELECTOR, selector)
                        if next_btn.is_displayed() and next_btn.is_enabled():
                            break
                    except NoSuchElementException:
                        continue

                if next_btn:
                    try:
                        driver.execute_script("arguments[0].click();", next_btn)
                        time.sleep(2)
                        continue
                    except Exception as e:
                        print(f"Error clicking next button: {e}")
                        break
                else:
                    # No next or submit button found, might be stuck
                    print(f"Could not find submit/next button for: {link}")
                    break

            # Close modal if still open
            time.sleep(2)
            close_selectors = [
                ".artdeco-modal__dismiss",
                "button[aria-label='Dismiss']",
                "//button[contains(@aria-label, 'Dismiss')]",
                "//button[@data-control-name='dismiss']"
            ]
            
            for selector in close_selectors:
                try:
                    if selector.startswith("//"):
                        close_btns = driver.find_elements(By.XPATH, selector)
                    else:
                        close_btns = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for btn in close_btns:
                        if btn.is_displayed():
                            try:
                                driver.execute_script("arguments[0].click();", btn)
                                time.sleep(1)
                            except:
                                pass
                except:
                    pass

        except Exception as e:
            print(f"Error processing job {link}: {e}")
            continue

    print(f"\nTotal jobs applied: {applied_count}/{len(job_links)}")
    return applied_count
