import os
from utils.helpers import get_driver, login, search_jobs, easy_apply


def main():
    email = os.getenv("LI_EMAIL")
    password = os.getenv("LI_PASSWORD")

    if not email or not password:
        raise Exception("LinkedIn credentials not found in environment variables")

    driver = get_driver()

    try:
        login(driver, email, password)
        search_jobs(driver, "DevOps Engineer", "India")
        applied = easy_apply(driver, max_apply=5)
        print(f"Applications submitted: {applied}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
