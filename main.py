from utils.helpers import login, search_jobs, apply_jobs
import os
import sys

def main():
    email = os.getenv("LI_EMAIL", "").strip()
    password = os.getenv("LI_PASSWORD", "").strip()
    
    # Validate credentials
    if not email or email == "YOUR_EMAIL" or not password or password == "YOUR_PASSWORD":
        print("ERROR: LinkedIn credentials are missing or not set!")
        print("Please set LI_EMAIL and LI_PASSWORD environment variables or GitHub Secrets.")
        print(f"LI_EMAIL is set: {bool(email and email != 'YOUR_EMAIL')}")
        print(f"LI_PASSWORD is set: {bool(password and password != 'YOUR_PASSWORD')}")
        sys.exit(1)
    
    keywords = ["DevOps Engineer"]
    location = "Bangalore, India"
    apply_limit = 5

    print(f"Starting LinkedIn automation for '{keywords[0]}'...")
    driver = login(email, password)
    job_links = search_jobs(driver, keywords, location)
    
    if not job_links:
        print("WARNING: No job links found. This might indicate:")
        print("  1. Login was unsuccessful")
        print("  2. LinkedIn is blocking automated access")
        print("  3. No jobs match the search criteria")
    else:
        print(f"Found {len(job_links)} total job links")
        apply_jobs(driver, job_links, apply_limit)
    
    print("All jobs processed successfully!")
    driver.quit()

if __name__ == "__main__":
    main()
