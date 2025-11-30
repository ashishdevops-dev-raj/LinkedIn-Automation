from utils.helpers import login, search_jobs, apply_jobs

def main():
    email = "YOUR_EMAIL"
    password = "YOUR_PASSWORD"
    keywords = ["DevOps Engineer", "Cloud Engineer"]
    location = "Bangalore, India"
    apply_limit = 5

    driver = login(email, password)
    job_links = search_jobs(driver, keywords, location)
    apply_jobs(driver, job_links, apply_limit)
    print("All jobs processed successfully!")
    driver.quit()

if __name__ == "__main__":
    main()
