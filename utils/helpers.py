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
    # Enable headless mode for CI environments
    import os
    if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--remote-debugging-port=9222")
    # Add user agent to appear more like a real browser
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    # Exclude automation flags
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # In CI environments, ChromeDriver should be in PATH from setup-chrome action
    # Otherwise, use ChromeDriverManager
    if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
        # Try to use ChromeDriver from PATH first, fallback to ChromeDriverManager
        try:
            import shutil
            chromedriver_path = shutil.which('chromedriver')
            if chromedriver_path:
                driver = webdriver.Chrome(
                    service=Service(chromedriver_path),
                    options=chrome_options
                )
            else:
                raise FileNotFoundError("ChromeDriver not in PATH")
        except Exception:
            # Fallback to ChromeDriverManager if system ChromeDriver not found
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
    else:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
    print("Loading LinkedIn login page...")
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)
    print("Login page loaded")

    # Fill in login credentials
    print("Waiting for username field...")
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    print("Filling in credentials...")
    password_field = driver.find_element(By.ID, "password")
    
    username_field.clear()
    username_field.send_keys(email)
    password_field.clear()
    password_field.send_keys(password)
    
    # Click login button
    print("Clicking login button...")
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()
    
    print(f"Login submitted for {email}")
    print("Waiting for page to redirect...")
    time.sleep(5)
    
    # Verify login was successful by checking if we're redirected away from login page
    current_url = driver.current_url
    print(f"Current URL after login: {current_url}")
    
    if "checkpoint" in current_url.lower() or "challenge" in current_url.lower():
        print("WARNING: LinkedIn is showing a security checkpoint/challenge page.")
        print("This usually means LinkedIn detected automated access.")
        print("Waiting 5 seconds to see if checkpoint resolves...")
        time.sleep(5)
        current_url = driver.current_url
        if "checkpoint" in current_url.lower() or "challenge" in current_url.lower():
            print("Checkpoint still present. Continuing anyway...")
    elif "login" in current_url.lower():
        print("WARNING: Still on login page. Login might have failed.")
    else:
        print(f"Login successful! Redirected to: {current_url}")
    
    return driver

def search_jobs(driver, keywords, location):
    all_job_links = []
    wait = WebDriverWait(driver, 20)

    for keyword in keywords:
        # Add filters: Easy Apply (f_EA=true) and Experience level 0-2 years (f_E=1,2)
        # f_E=1 means 0-1 years, f_E=2 means 1-2 years, so we use both
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword.replace(' ', '%20')}&location={location.replace(' ', '%20')}&f_EA=true&f_E=1%2C2"
        print(f"Searching for '{keyword}' in {location}...")
        print("Filters: Easy Apply only, 0-2 years experience")
        print(f"Loading URL: {search_url}")
        driver.get(search_url)
        
        # Wait for page to load - check if checkpoint page
        print("Waiting for job search page to load...")
        time.sleep(5)
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        if "checkpoint" in current_url.lower() or "challenge" in current_url.lower():
            print("WARNING: Still on checkpoint page. Cannot search for jobs.")
            continue
        
        # Wait for job results container to appear
        print("Looking for job results container...")
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-results-list, .scaffold-layout__list-container, ul.jobs-search__results-list")))
            print("Job results container found")
        except TimeoutException:
            print("WARNING: Job results container not found. Trying to continue anyway...")
        
        # Scroll down gradually to load more job listings
        print("Scrolling to load job listings...")
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * " + str((i + 1) / 3) + ");")
            time.sleep(1)
        
        # Wait a bit more for dynamic content to load
        print("Waiting for dynamic content to load...")
        time.sleep(2)
        
        # Try multiple selectors for job cards (LinkedIn changes these frequently)
        print("Searching for job cards...")
        job_cards = []
        selectors = [
            "div.job-card-container",
            "li.job-card-list__entity-lockup",
            "div[data-job-id]",
            ".job-card-list__entity-lockup",
            "li.jobs-search-results__list-item",
            ".jobs-search-results__list-item",
            "div.job-card-container--clickable",
            "a.job-card-list__title",
            "div.base-card"
        ]
        
        for selector in selectors:
            try:
                print(f"  Trying selector: {selector}")
                job_cards = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_cards and len(job_cards) > 0:
                    print(f"✓ Found {len(job_cards)} job listings for '{keyword}' using selector: {selector}")
                    break
            except Exception as e:
                print(f"  Selector {selector} failed: {str(e)[:50]}")
                continue
        
        # If still no job cards, try finding by job links directly
        if not job_cards or len(job_cards) == 0:
            print("No job cards found. Trying alternative method: searching for job links directly...")
            try:
                job_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/jobs/view/']")
                if job_links:
                    print(f"✓ Found {len(job_links)} job links directly")
                    for link_elem in job_links:
                        link = link_elem.get_attribute("href")
                        if link and link not in all_job_links and "/jobs/view/" in link:
                            all_job_links.append(link)
                    print(f"Total unique job links collected: {len(all_job_links)}")
                    continue
            except Exception as e:
                print(f"Alternative method also failed: {str(e)[:50]}")
                pass
        
        if not job_cards or len(job_cards) == 0:
            print(f"WARNING: No job cards found for '{keyword}'. Current URL: {driver.current_url}")
            print("Page title:", driver.title)
            # Try to get page source snippet for debugging
            try:
                page_source = driver.page_source[:500]
                if "checkpoint" in page_source.lower() or "challenge" in page_source.lower():
                    print("Checkpoint/challenge detected in page source")
            except:
                pass
            continue

        print(f"Extracting links from {len(job_cards)} job cards...")
        for idx, job in enumerate(job_cards, 1):
            try:
                # Try to find link in various ways
                link = None
                # Method 1: Find anchor tag within job card
                try:
                    link_elements = job.find_elements(By.TAG_NAME, "a")
                    for link_elem in link_elements:
                        href = link_elem.get_attribute("href")
                        if href and "/jobs/view/" in href:
                            link = href
                            break
                except:
                    pass
                
                # Method 2: Try finding by data attributes
                if not link:
                    try:
                        job_id = job.get_attribute("data-job-id")
                        if job_id:
                            link = f"https://www.linkedin.com/jobs/view/{job_id}"
                    except:
                        pass
                
                # Method 3: Try finding parent link
                if not link:
                    try:
                        parent = job.find_element(By.XPATH, "./ancestor::a[contains(@href, '/jobs/view/')]")
                        link = parent.get_attribute("href")
                    except:
                        pass
                
                if link and link not in all_job_links and "/jobs/view/" in link:
                    all_job_links.append(link)
                    if idx % 5 == 0:
                        print(f"  Processed {idx}/{len(job_cards)} job cards, found {len(all_job_links)} unique links")
            except Exception as e:
                continue
        
        print(f"Completed processing '{keyword}'. Total links so far: {len(all_job_links)}")

    print(f"Job search complete. Found {len(all_job_links)} total unique job links")
    return all_job_links

def check_experience_level(driver):
    """Check if job requires 0-2 years of experience"""
    try:
        # Look for experience level in job description or criteria
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        
        # Check for experience indicators
        experience_keywords = [
            "0-2 years",
            "0 to 2 years",
            "1-2 years",
            "1 to 2 years",
            "entry level",
            "junior",
            "0-1 years",
            "0 to 1 years",
            "fresher",
            "0 years",
            "1 year"
        ]
        
        # Also check for higher experience that would exclude this
        exclude_keywords = [
            "3+ years",
            "3-5 years",
            "5+ years",
            "senior",
            "lead",
            "principal",
            "4+ years"
        ]
        
        # If we find exclude keywords, it's not 0-2 years
        for exclude in exclude_keywords:
            if exclude in page_text:
                return False
        
        # Check if any experience keywords match
        for keyword in experience_keywords:
            if keyword in page_text:
                return True
        
        # Try to find experience in structured data
        try:
            criteria_sections = driver.find_elements(By.CSS_SELECTOR, ".jobs-description__job-criteria-item, .jobs-unified-top-card__job-insight")
            for criteria in criteria_sections:
                text = criteria.text.lower()
                if "experience" in text or "years" in text:
                    # Check if it matches 0-2 years
                    for keyword in experience_keywords:
                        if keyword in text:
                            return True
                    # Check if it's higher than 2 years
                    for exclude in exclude_keywords:
                        if exclude in text:
                            return False
        except:
            pass
        
        # If we can't determine, assume it might be okay (since URL filter should handle it)
        return True
    except Exception as e:
        print(f"  Could not verify experience level: {str(e)[:50]}")
        # If we can't check, assume it's okay (URL filter should handle it)
        return True

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
            
            # Verify experience level (0-2 years)
            print(f"Checking experience level for job: {link}")
            if not check_experience_level(driver):
                print(f"  Job requires more than 2 years experience. Skipping...")
                continue
            print(f"  Experience level verified (0-2 years)")

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
