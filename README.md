# LinkedIn Job Application Automation

Automates LinkedIn job applications using Selenium. This bot searches for jobs matching your criteria and automatically applies to them using LinkedIn's Easy Apply feature.

## 🎯 Features

- **Automated Job Search**: Searches for jobs based on keywords and location
- **Smart Filtering**: 
  - Easy Apply jobs only
  - Entry level positions (0-2 years experience)
  - Recently posted jobs (within the past week)
- **Daily Limit**: Applies to maximum 10 jobs per day
- **Duplicate Prevention**: Tracks applied jobs to avoid duplicates
- **Session Management**: Supports cookie-based authentication to avoid checkpoints
- **Experience Verification**: Double-checks experience requirements before applying

## 📋 Prerequisites

- Python 3.11 or higher
- LinkedIn account
- Google Chrome browser
- Git (for cloning the repository)

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/ashishdevops-dev-raj/LinkedIn-Automation.git
cd LinkedIn-Automation
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `selenium` - For browser automation
- `webdriver-manager` - For managing ChromeDriver
- `pyyaml` - For configuration files
- `pandas` - For data handling

### Step 3: Install Chrome Browser

Make sure Google Chrome is installed on your system. The script will automatically download the appropriate ChromeDriver.

## ⚙️ Configuration

### Option 1: Using Environment Variables (Recommended for Local Testing)

Create a `.env` file in the project root (or set environment variables):

```bash
LI_EMAIL=your_email@example.com
LI_PASSWORD=your_password
COOKIES_B64=your_base64_encoded_cookies  # Optional but recommended
```

### Option 2: Using GitHub Secrets (For GitHub Actions)

See the "GitHub Actions Setup" section below.

## 🔐 Getting LinkedIn Cookies (Recommended)

Using cookies helps avoid LinkedIn's security checkpoints and makes the automation more reliable.

### Step 1: Export Cookies from Browser

1. **Log into LinkedIn** in your Chrome browser
2. **Open Developer Tools** (F12 or Right-click → Inspect)
3. Go to **Application** tab (or **Storage** in Firefox)
4. Click on **Cookies** → `https://www.linkedin.com`
5. **Copy the important cookies**:
   - `li_at` (LinkedIn authentication token)
   - `JSESSIONID` (Session ID)
   - Any other cookies that look important

### Step 2: Create Cookies JSON File

Create a file with your cookies in this format:

```json
[
  {
    "name": "li_at",
    "value": "your_li_at_value_here",
    "domain": ".linkedin.com",
    "path": "/",
    "secure": true,
    "httpOnly": true
  },
  {
    "name": "JSESSIONID",
    "value": "your_session_id_here",
    "domain": ".linkedin.com",
    "path": "/",
    "secure": true,
    "httpOnly": true
  }
]
```

### Step 3: Encode to Base64

**Using Python:**
```python
import json
import base64

# Read your cookies JSON file
with open('cookies.json', 'r') as f:
    cookies = json.load(f)

# Encode to base64
cookies_json = json.dumps(cookies)
cookies_b64 = base64.b64encode(cookies_json.encode('utf-8')).decode('utf-8')

print(cookies_b64)
```

**Using Online Tool:**
- Go to https://www.base64encode.org/
- Paste your JSON cookies
- Click "Encode"
- Copy the result

### Step 4: Add to Environment Variables

Add the base64-encoded cookies to your environment:

```bash
export COOKIES_B64="your_base64_encoded_string_here"
```

Or add it to your `.env` file.

## 🏃 Running Locally

### Step 1: Set Environment Variables

**Windows (PowerShell):**
```powershell
$env:LI_EMAIL="your_email@example.com"
$env:LI_PASSWORD="your_password"
$env:COOKIES_B64="your_base64_cookies"  # Optional
```

**Windows (Command Prompt):**
```cmd
set LI_EMAIL=your_email@example.com
set LI_PASSWORD=your_password
set COOKIES_B64=your_base64_cookies  # Optional
```

**Linux/Mac:**
```bash
export LI_EMAIL="your_email@example.com"
export LI_PASSWORD="your_password"
export COOKIES_B64="your_base64_cookies"  # Optional
```

### Step 2: Run the Script

```bash
python main.py
```

The script will:
1. Log into LinkedIn (or restore session using cookies)
2. Search for jobs matching your criteria
3. Apply to up to 10 jobs per day
4. Track applied jobs to avoid duplicates

## 🔧 Customization

### Change Job Search Criteria

Edit `main.py` to customize:

```python
keywords = ["DevOps Engineer"]  # Change job keywords
location = "Bangalore, India"   # Change location
apply_limit = 5                 # Maximum jobs to process (daily limit is 10)
```

### Change Daily Application Limit

Edit `utils/helpers.py`:

```python
daily_limit = 10  # Change this value
```

### Modify Filters

The script filters for:
- Easy Apply jobs only (`f_EA=true`)
- Entry level (0-2 years) (`f_E=2`)
- Recently posted (past week) (`f_TPR=r604800`)

To modify filters, edit the `search_jobs` function in `utils/helpers.py`.

## 🚀 GitHub Actions Setup

### Step 1: Fork/Clone the Repository

Make sure you have the repository on GitHub.

### Step 2: Add GitHub Secrets

1. Go to your repository on GitHub
2. Click on **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

   **Required:**
   - **Name**: `LI_EMAIL`
     - **Value**: Your LinkedIn email address
   
   - **Name**: `LI_PASSWORD`
     - **Value**: Your LinkedIn password

   **Optional (but recommended):**
   - **Name**: `COOKIES_B64`
     - **Value**: Your base64-encoded LinkedIn cookies (see "Getting LinkedIn Cookies" section above)

### Step 3: Trigger the Workflow

The workflow runs automatically on:
- **Push to main branch**
- **Manual trigger** (Workflow Dispatch)

To manually trigger:
1. Go to **Actions** tab
2. Select **LinkedIn Quick_Apply** workflow
3. Click **Run workflow**
4. Click the green **Run workflow** button

### Step 4: Monitor Execution

1. Go to **Actions** tab
2. Click on the latest workflow run
3. Click on **apply-jobs** job
4. View the logs to see progress

## 📊 How It Works

1. **Login**: 
   - First tries to restore session using cookies (if provided)
   - Falls back to email/password login if cookies fail

2. **Job Search**:
   - Searches LinkedIn jobs with your keywords and location
   - Applies filters: Easy Apply, Entry level, Recently posted
   - Extracts job links from search results

3. **Application Process**:
   - For each job:
     - Loads the job page
     - Checks for Easy Apply button
     - Verifies experience level (0-2 years)
     - Clicks Easy Apply button
     - Fills out the application form
     - Submits the application
   - Tracks applied jobs to prevent duplicates
   - Stops after reaching daily limit (10 applications)

4. **Tracking**:
   - Saves applied jobs to `applied_jobs.json`
   - Resets daily limit each day
   - Prevents applying to the same job twice

## 📁 Project Structure

```
LinkedIn-Automation/
├── .github/
│   └── workflows/
│       └── github_actions.yaml    # GitHub Actions workflow
├── utils/
│   ├── helpers.py                 # Main automation logic
│   └── __init__.py
├── main.py                        # Entry point
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── .gitignore                     # Git ignore rules
```

## 🐛 Troubleshooting

### Issue: "ChromeDriver not found"

**Solution**: The script uses `webdriver-manager` which automatically downloads ChromeDriver. Make sure you have internet connection.

### Issue: "LinkedIn checkpoint/challenge page"

**Solution**: 
- Use `COOKIES_B64` to restore your session (recommended)
- LinkedIn may detect automation - using cookies helps avoid this
- Try running at different times

### Issue: "No job links found"

**Possible causes**:
- Login failed (check credentials)
- LinkedIn is blocking access (use cookies)
- No jobs match your criteria (try different keywords/location)

### Issue: "Easy Apply not available"

**Possible causes**:
- Job doesn't have Easy Apply option
- Page didn't load completely (check internet connection)
- LinkedIn changed their page structure

### Issue: "Daily limit reached"

**Solution**: This is normal. The script applies to maximum 10 jobs per day. The limit resets at midnight.

## ⚠️ Important Notes

1. **Rate Limiting**: Don't run the script too frequently. LinkedIn may flag your account for suspicious activity.

2. **Account Safety**: 
   - Use cookies when possible to avoid checkpoints
   - Don't share your credentials or cookies publicly
   - Monitor your LinkedIn account for any issues

3. **Job Quality**: 
   - Review the jobs the script finds before running
   - Customize keywords and location to match your preferences
   - The script applies automatically - make sure you want to apply to these jobs

4. **Legal Compliance**: 
   - Ensure you comply with LinkedIn's Terms of Service
   - Use automation responsibly
   - Don't abuse the system

## 📝 License

This project is for educational purposes. Use at your own risk.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📧 Support

If you encounter any issues:
1. Check the Troubleshooting section
2. Review the GitHub Actions logs
3. Open an issue on GitHub

---

**Happy Job Hunting! 🎯**
