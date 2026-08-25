# 🏥 Doctor Lead Generation System - Complete Setup Guide

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Automation](#automation)
7. [Dashboard](#dashboard)
8. [Troubleshooting](#troubleshooting)
9. [Legal & Compliance](#legal--compliance)

---

## 🎯 System Overview

This system automates the entire doctor lead generation and outreach process:

```
Lead Generation → Email Finding → LinkedIn Outreach → Email Campaign → Call Follow-up
```

**Key Features:**
- ✅ AI-powered lead generation using DeepSeek V3.1
- ✅ Automated email discovery
- ✅ LinkedIn automation (connection requests + messaging)
- ✅ Email campaigns with AI-generated content
- ✅ Voice call campaigns (Twilio integration)
- ✅ CRM database with SQLite
- ✅ Real-time analytics dashboard
- ✅ Automated scheduling

---

## 📦 Prerequisites

### Required Accounts (All Free Tiers Available)

1. **OpenRouter Account** (for DeepSeek AI)
   - Sign up: https://openrouter.ai/
   - Get API key: https://openrouter.ai/keys
   - Free credits provided on signup

2. **LinkedIn Account** (for outreach)
   - ⚠️ **IMPORTANT**: Use a burner/secondary account
   - Not your main professional LinkedIn
   - Risk of account restrictions

3. **Twilio Account** (for calls - optional)
   - Sign up: https://www.twilio.com/try-twilio
   - $15 free trial credit
   - Get phone number + credentials

4. **Hunter.io Account** (for email finding - optional)
   - Sign up: https://hunter.io/
   - 25 free searches/month
   - Optional: can use pattern matching instead

### System Requirements

- Python 3.8 or higher
- Chrome/Chromium browser (for LinkedIn automation)
- 2GB RAM minimum
- Internet connection

---

## 🔧 Installation

### Step 1: Clone/Download the Project

```bash
# Create project directory
mkdir doctor-lead-gen
cd doctor-lead-gen

# Download all files (main.py, dashboard.py, scheduler.py, requirements.txt, .env.example)
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# If you encounter issues, install individually:
pip install requests selenium undetected-chromedriver beautifulsoup4
pip install twilio fastapi uvicorn apscheduler
pip install email-validator pandas tqdm colorama
```

### Step 4: Setup ChromeDriver

```bash
# ChromeDriver is auto-installed by undetected-chromedriver
# But ensure Chrome browser is installed on your system
```

---

## ⚙️ Configuration

### Step 1: Create Configuration File

```bash
# Copy the example env file
cp .env.example .env

# Edit the file
nano .env  # or use any text editor
```

### Step 2: Add Your API Keys

Open `.env` and fill in your credentials:

```bash
# OpenRouter (REQUIRED)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx

# LinkedIn (REQUIRED for LinkedIn outreach)
LINKEDIN_EMAIL=your_burner_email@gmail.com
LINKEDIN_PASSWORD=your_secure_password

# Twilio (OPTIONAL for calls)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE=+1234567890

# Hunter.io (OPTIONAL for better email finding)
HUNTER_API_KEY=your_hunter_key
```

### Step 3: Update main.py Configuration

Edit the `Config` class in `main.py`:

```python
class Config:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
    LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
    # ... etc
```

---

## 🚀 Usage

### Quick Start (Manual Mode)

#### 1. Run a Test Campaign

```bash
python main.py
```

This will:
- Generate 50 cardiologist leads in New York
- Find their emails
- Search for LinkedIn profiles
- Send 20 LinkedIn connection requests
- Prepare 30 emails
- Make 10 test calls (if Twilio configured)

#### 2. Customize the Campaign

Edit the `main.py` file at the bottom:

```python
if __name__ == "__main__":
    orchestrator = OutreachOrchestrator()
    
    # Change specialty and location
    orchestrator.run_full_campaign(
        specialty="Orthopedic Surgeon",  # Change specialty
        location="Los Angeles, CA"        # Change location
    )
```

#### 3. Run Individual Components

```python
from main import OutreachOrchestrator

orchestrator = OutreachOrchestrator()

# Only generate leads
orchestrator.generate_leads("Cardiologist", "New York, NY", count=100)

# Only find emails
orchestrator.enrich_leads()

# Only LinkedIn outreach
orchestrator.linkedin_outreach(limit=50)

# Only email campaign
orchestrator.email_campaign(limit=100)

# Only calls
orchestrator.call_campaign(limit=20)
```

---

## ⏰ Automation

### Run Automated Scheduler

The scheduler runs campaigns automatically at optimal times throughout the day:

```bash
# Start the scheduler
python scheduler.py
```

**Default Schedule:**
- **8:00 AM**: Generate new leads (50 per day)
- **9:00 AM**: Enrich leads (find emails + LinkedIn)
- **10:00 AM, 2:00 PM, 5:00 PM**: LinkedIn outreach batches (20 each)
- **10:30 AM, 1:00 PM, 3:30 PM, 6:00 PM**: Email campaigns (30 each)
- **2:30 PM, 4:30 PM**: Call campaigns (10 each)
- **Every Monday 9:00 AM**: Weekly performance report

### Test the Scheduler

```bash
# Run a test campaign immediately
python scheduler.py test
```

### Run as Background Service

#### On Linux/Mac:

```bash
# Create a systemd service
sudo nano /etc/systemd/system/doctor-leads.service

# Add:
[Unit]
Description=Doctor Lead Generation Scheduler
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/doctor-lead-gen
ExecStart=/path/to/doctor-lead-gen/venv/bin/python scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable doctor-leads
sudo systemctl start doctor-leads
```

#### On Windows:

Use Task Scheduler:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., "At startup")
4. Action: Start program
5. Program: `C:\path\to\venv\Scripts\python.exe`
6. Arguments: `C:\path\to\scheduler.py`

---

## 📊 Dashboard

### Start the Analytics Dashboard

```bash
# Start the dashboard server
python dashboard.py
```

**Access at:** http://localhost:8000

### Dashboard Features:

- **Real-time Statistics**: Total leads, emails sent, LinkedIn requests, calls made
- **Lead Status Breakdown**: Visual breakdown of pipeline stages
- **Top Specialties**: Most targeted doctor specialties
- **Recent Activity**: Latest outreach actions
- **Daily Activity Chart**: 7-day activity trend
- **Auto-refresh**: Updates every 30 seconds

### API Endpoints:

```bash
# Get statistics JSON
curl http://localhost:8000/api/stats

# Response:
{
  "total_leads": 150,
  "status_breakdown": {
    "new": 20,
    "enriched": 30,
    "linkedin_sent": 40,
    "email_sent": 35,
    "called": 25
  },
  "conversion_rates": {
    "email_rate": 23.3,
    "linkedin_rate": 26.7,
    "call_rate": 16.7
  },
  "top_specialties": [
    ["Cardiologist", 50],
    ["Orthopedic Surgeon", 30],
    ["Neurologist", 25]
  ]
}
```

---

## 🔍 Database Management

### View Database Contents

```python
import sqlite3

# Connect to database
conn = sqlite3.connect('doctor_leads.db')
cursor = conn.cursor()

# View all leads
cursor.execute("SELECT * FROM leads")
for row in cursor.fetchall():
    print(row)

# View outreach activity
cursor.execute("SELECT * FROM outreach")
for row in cursor.fetchall():
    print(row)

# Export to CSV
import pandas as pd
df = pd.read_sql_query("SELECT * FROM leads", conn)
df.to_csv('leads_export.csv', index=False)
```

### Database Schema

**Leads Table:**
```sql
CREATE TABLE leads (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    specialty TEXT,
    location TEXT,
    hospital TEXT,
    phone TEXT,
    email TEXT,
    linkedin_url TEXT,
    status TEXT DEFAULT 'new',
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

**Outreach Table:**
```sql
CREATE TABLE outreach (
    id INTEGER PRIMARY KEY,
    lead_id INTEGER,
    channel TEXT,  -- 'email', 'linkedin', 'call'
    message TEXT,
    status TEXT,
    response TEXT,
    sent_at TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads (id)
)
```

---

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### 1. OpenRouter API Errors

**Problem:** "Invalid API key" or "Rate limit exceeded"

**Solution:**
```bash
# Check your API key is correct
echo $OPENROUTER_API_KEY

# Verify it starts with 'sk-or-v1-'
# Check balance at: https://openrouter.ai/account

# If rate limited, wait or upgrade plan
```

#### 2. LinkedIn Login Fails

**Problem:** "Login failed" or "CAPTCHA detected"

**Solution:**
- Use a fresh LinkedIn account
- Login manually first in your browser
- Disable 2FA on the burner account
- Add delays between requests
- Consider using LinkedIn's official API (paid)

```python
# Increase delays in code
time.sleep(10)  # Wait longer between actions
```

#### 3. ChromeDriver Issues

**Problem:** "chromedriver not found" or version mismatch

**Solution:**
```bash
# Uninstall and reinstall
pip uninstall undetected-chromedriver
pip install undetected-chromedriver

# Or specify Chrome path manually
from selenium import webdriver
options.binary_location = "/path/to/chrome"
```

#### 4. Email Finding Returns No Results

**Problem:** Pattern matching not finding emails

**Solution:**
- Sign up for Hunter.io (25 free searches/month)
- Use multiple email verification services
- Implement more email patterns

```python
# Add more patterns
patterns = [
    f"{first}.{last}@{domain}",
    f"{first}{last}@{domain}",
    f"dr.{first}.{last}@{domain}",
    f"{first[0]}.{last}@{domain}",
    # Add more variations
]
```

#### 5. Twilio Call Errors

**Problem:** "Unable to create call" or "Insufficient balance"

**Solution:**
- Verify phone number is verified in Twilio
- Check trial balance: https://console.twilio.com/
- Ensure "from" number is a Twilio number
- Add country code to recipient number

```python
# Format phone correctly
phone = "+1234567890"  # Include country code
```

#### 6. Database Locked Error

**Problem:** "Database is locked"

**Solution:**
```python
# Increase timeout
conn = sqlite3.connect('doctor_leads.db', timeout=20)

# Or use check_same_thread=False
conn = sqlite3.connect('doctor_leads.db', check_same_thread=False)
```

#### 7. Memory Issues

**Problem:** System runs out of memory

**Solution:**
- Process leads in smaller batches
- Close browser after each batch
- Clear variables

```python
# Process in batches
for i in range(0, total_leads, 10):
    batch = leads[i:i+10]
    process_batch(batch)
    
    # Cleanup
    linkedin.close()
    linkedin = LinkedInAutomation()
```

---

## 📈 Optimization Tips

### 1. Improve Lead Quality

```python
# Add priority scoring in AI prompt
prompt = f"""Generate doctor profiles with priority scoring.
Factors for high priority:
- Private practice owners
- Decision makers
- High patient volume
- Specialty relevance: {specialty}
"""
```

### 2. Better Email Patterns

```python
# Use common hospital domains
COMMON_HOSPITAL_DOMAINS = [
    "mayoclinic.org",
    "clevelandclinic.org",
    "jhmi.edu",
    "med.cornell.edu"
]

# Check against known patterns
def smart_email_guess(name, hospital):
    # Implementation here
    pass
```

### 3. A/B Test Messages

```python
# Generate multiple message variants
message_a = ai.generate_linkedin_message(name, specialty)
message_b = ai.generate_linkedin_message_variant_b(name, specialty)

# Track which performs better
if random.random() < 0.5:
    send_message(message_a, variant='A')
else:
    send_message(message_b, variant='B')
```

### 4. Rate Limit Management

```python
from time import sleep
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_per_hour):
        self.max_per_hour = max_per_hour
        self.requests = []
    
    def wait_if_needed(self):
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        # Remove old requests
        self.requests = [r for r in self.requests if r > hour_ago]
        
        if len(self.requests) >= self.max_per_hour:
            sleep_time = (self.requests[0] - hour_ago).total_seconds()
            sleep(sleep_time)
        
        self.requests.append(now)
```

---

## 📧 Email Campaign Setup (Optional)

### Using Gmail SMTP

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_smtp(to_email, subject, body):
    # Setup
    sender = os.getenv("SMTP_EMAIL")
    password = os.getenv("SMTP_PASSWORD")  # Use App Password
    
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    
    # Send
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
```

**Setup Gmail App Password:**
1. Go to Google Account settings
2. Security → 2-Step Verification
3. App passwords → Generate
4. Use that password in .env

### Using SendGrid (Better for bulk)

```bash
pip install sendgrid
```

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email_sendgrid(to_email, subject, body):
    message = Mail(
        from_email='your@email.com',
        to_emails=to_email,
        subject=subject,
        html_content=body
    )
    
    sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
    response = sg.send(message)
```

---

## ⚖️ Legal & Compliance

### IMPORTANT DISCLAIMERS

⚠️ **READ BEFORE USING**

1. **CAN-SPAM Act Compliance (USA)**
   - Include physical mailing address in emails
   - Add unsubscribe link to all emails
   - Honor opt-out requests within 10 days
   - Don't use deceptive subject lines

2. **GDPR Compliance (EU)**
   - Obtain consent before contacting
   - Provide data deletion options
   - Maintain records of consent
   - Honor right to be forgotten

3. **TCPA Compliance (USA Calls)**
   - Don't call numbers on Do Not Call list
   - Call only 8 AM - 9 PM local time
   - Identify yourself clearly
   - Maintain internal DNC list

4. **LinkedIn Terms of Service**
   - Automation may violate TOS
   - Risk of account restriction/ban
   - Use burner accounts only
   - Consider official API access

5. **Medical Privacy (HIPAA)**
   - Don't request/store patient data
   - Focus on business outreach only
   - No medical record access

### Best Practices

```python
# Add unsubscribe to emails
email_footer = """
<p>---</p>
<p>To unsubscribe, reply with 'UNSUBSCRIBE'</p>
<p>Your Company Name<br>
123 Street Address<br>
City, State ZIP</p>
"""

# Maintain DNC list
DNC_LIST = set()

def is_dnc(phone):
    return phone in DNC_LIST

def add_to_dnc(phone):
    DNC_LIST.add(phone)
    # Also save to database
```

---

## 🔐 Security Best Practices

### 1. Protect API Keys

```bash
# Never commit .env file
echo ".env" >> .gitignore

# Use environment variables in production
export OPENROUTER_API_KEY="your-key"
```

### 2. Use Burner Accounts

- Create separate email for automation
- Use VPN for LinkedIn automation
- Don't use your main professional accounts

### 3. Encrypt Database

```python
# Use SQLCipher for encrypted database
from pysqlcipher3 import dbapi2 as sqlite

conn = sqlite.connect('leads.db')
conn.execute('PRAGMA key="your-encryption-key"')
```

### 4. Rate Limiting

```python
# Implement exponential backoff
def retry_with_backoff(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i == max_retries - 1:
                raise
            sleep(2 ** i)
```

---

## 📚 Additional Resources

### Documentation Links

- **OpenRouter Docs**: https://openrouter.ai/docs
- **DeepSeek Model**: https://deepseek.com/
- **Selenium Docs**: https://selenium-python.readthedocs.io/
- **Twilio Docs**: https://www.twilio.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/

### Useful Commands

```bash
# Check Python version
python --version

# List installed packages
pip list

# Check database size
ls -lh doctor_leads.db

# View logs
tail -f campaign_scheduler.log

# Backup database
cp doctor_leads.db doctor_leads_backup_$(date +%Y%m%d).db

# Export leads to CSV
sqlite3 doctor_leads.db ".mode csv" ".output leads.csv" "SELECT * FROM leads;"
```

---

## 🎯 Next Steps

1. **Start Small**: Test with 10 leads first
2. **Monitor Results**: Track open rates, responses
3. **Optimize Messages**: A/B test different approaches
4. **Scale Gradually**: Increase volume slowly
5. **Stay Compliant**: Follow all regulations
6. **Personalize**: Use AI to customize each message
7. **Follow Up**: Track responses and engage

---

## 💡 Advanced Customization

### Custom Lead Sources

```python
# Add your own lead scraper
class CustomScraper:
    def scrape_custom_source(self, specialty, location):
        # Your implementation
        leads = []
        # ... scraping logic
        return leads
```

### Custom AI Prompts

```python
# Customize message generation
def generate_custom_message(name, specialty, context):
    prompt = f"""Create a message for Dr. {name}.
    Context: {context}
    Tone: Professional but warm
    Include: Recent research in {specialty}
    """
    return ai.call_deepseek(prompt)
```

### Webhook Integration

```python
# Send updates to external systems
import requests

def send_webhook(event, data):
    webhook_url = "https://your-system.com/webhook"
    requests.post(webhook_url, json={
        "event": event,
        "data": data,
        "timestamp": datetime.now().isoformat()
    })
```

---

## 🤝 Support & Community

### Getting Help

1. Check this documentation first
2. Review error logs
3. Search existing issues
4. Ask in community forums

### Contributing

Want to improve this system? Consider:
- Better scraping methods
- More email patterns
- Enhanced AI prompts
- Additional integrations

---

## 📝 License & Disclaimer

This software is provided "as is" for educational purposes. Users are responsible for:
- Complying with all applicable laws
- Respecting platform Terms of Service
- Obtaining necessary permissions
- Protecting data privacy

**Use responsibly and ethically!**

---

*Last Updated: 2025-10-20*
*Version: 1.0*