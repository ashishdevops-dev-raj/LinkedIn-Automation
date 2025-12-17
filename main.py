from utils.helpers import login, search_jobs, apply_jobs
import os
import sys

# Force output to flush immediately for real-time logging in CI
import functools
print = functools.partial(print, flush=True)

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
    apply_limit = 5  # This is now just a maximum, daily limit is 5

    print(f"Starting LinkedIn automation for '{keywords[0]}'...")
    print("Filters: Easy Apply only, 0-2 years experience, Recently Posted (Past week)")
    print("Step 1: Logging into LinkedIn...")
    
    # Check for cookies
    cookies_b64 = os.getenv("COOKIES_B64", "").strip()
    if cookies_b64:
        print("COOKIES_B64 found. Will attempt to use cookies for session restoration.")
    else:
        print("No COOKIES_B64 provided. Will use email/password login.")
    
    driver = login(email, password, cookies_b64 if cookies_b64 else None)
    print("Step 2: Searching for jobs with filters (Easy Apply, 0-2 years exp)...")
    job_links = search_jobs(driver, keywords, location)
    
    if not job_links:
        print("WARNING: No job links found. This might indicate:")
        print("  1. Login was unsuccessful")
        print("  2. LinkedIn is blocking automated access")
        print("  3. No jobs match the search criteria")
    else:
        print(f"Found {len(job_links)} total job links")
        print("Step 3: Starting job application process...")
        apply_jobs(driver, job_links, apply_limit)
    
    print("All jobs processed successfully!")
    driver.quit()

if __name__ == "__main__":
    main()
