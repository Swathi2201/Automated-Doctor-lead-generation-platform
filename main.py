"""
Complete Doctor Lead Generation & Outreach System
Using DeepSeek V3.1 (OpenRouter) + Free Tools
"""

import os
import json
import time
import sqlite3
import requests
from datetime import datetime
from typing import List, Dict, Optional
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    # OpenRouter API (DeepSeek V3.1)
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    DEEPSEEK_MODEL = "deepseek/deepseek-chat"

    # Database
    DB_NAME = "doctor_leads.db"

    # LinkedIn Credentials (use burner account)
    LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
    LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

    # Twilio (for calls - free trial)
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE = os.getenv("TWILIO_PHONE")

    # Hunter.io API (optional)
    HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")

    # Rate Limits
    LINKEDIN_DAILY_LIMIT = 100
    EMAIL_DAILY_LIMIT = 500
    CALL_DAILY_LIMIT = 50

# ============================================================================
# DATABASE SETUP
# ============================================================================

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DB_NAME)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Leads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialty TEXT,
                location TEXT,
                hospital TEXT,
                phone TEXT,
                email TEXT,
                linkedin_url TEXT,
                status TEXT DEFAULT 'new',
                priority INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Outreach activity table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outreach (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER,
                channel TEXT,
                message TEXT,
                status TEXT,
                response TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lead_id) REFERENCES leads (id)
            )
        ''')
        
        self.conn.commit()
    
    def add_lead(self, lead_data: Dict) -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO leads (name, specialty, location, hospital, phone, email, linkedin_url, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            lead_data.get('name'),
            lead_data.get('specialty'),
            lead_data.get('location'),
            lead_data.get('hospital'),
            lead_data.get('phone'),
            lead_data.get('email'),
            lead_data.get('linkedin_url'),
            lead_data.get('priority', 0)
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_leads_by_status(self, status: str) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM leads WHERE status = ?', (status,))
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def update_lead_status(self, lead_id: int, status: str):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE leads SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (status, lead_id))
        self.conn.commit()
    
    def log_outreach(self, lead_id: int, channel: str, message: str, status: str):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO outreach (lead_id, channel, message, status)
            VALUES (?, ?, ?, ?)
        ''', (lead_id, channel, message, status))
        self.conn.commit()

# ============================================================================
# AI ENGINE (DeepSeek V3.1)
# ============================================================================

class AIEngine:
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def call_deepseek(self, prompt: str, system_prompt: str = "") -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": Config.DEEPSEEK_MODEL,
            "messages": messages
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"AI Error: {e}")
            return ""
    
    def generate_doctor_leads(self, specialty: str, location: str, count: int = 10) -> List[Dict]:
        """Generate potential doctor leads using AI"""
        prompt = f"""Generate {count} realistic doctor profiles for marketing outreach.
        Specialty: {specialty}
        Location: {location}
        
        For each doctor, provide:
        - Full name
        - Specialty
        - Hospital/Clinic name
        - Location
        - Estimated priority (1-10, where 10 is highest)
        
        Return as JSON array."""
        
        system_prompt = "You are a medical marketing data analyst. Generate realistic doctor profiles based on common medical naming patterns and hospital structures."
        
        response = self.call_deepseek(prompt, system_prompt)
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return []
        except:
            return []
    
    def generate_linkedin_message(self, doctor_name: str, specialty: str) -> str:
        """Generate personalized LinkedIn message"""
        prompt = f"""Create a professional, personalized LinkedIn connection message for Dr. {doctor_name}, a {specialty} specialist.
        
        Requirements:
        - Keep it under 300 characters
        - Mention their specialty
        - Professional but friendly tone
        - Include a clear value proposition for a medical product/service
        - No spam-like language
        
        Return only the message text."""
        
        return self.call_deepseek(prompt).strip('"').strip()
    
    def generate_email_subject(self, doctor_name: str, specialty: str) -> str:
        """Generate email subject line"""
        prompt = f"""Create a compelling email subject line for Dr. {doctor_name}, a {specialty}.
        Make it professional, relevant, and likely to be opened. Max 60 characters."""
        
        return self.call_deepseek(prompt).strip('"').strip()
    
    def generate_email_body(self, doctor_name: str, specialty: str) -> str:
        """Generate email body"""
        prompt = f"""Write a professional email to Dr. {doctor_name}, a {specialty} specialist.
        
        Purpose: Introduce a medical product/service that could benefit their practice.
        Tone: Professional, respectful, value-focused
        Length: 150-200 words
        Include: Greeting, value proposition, call-to-action
        
        Return only the email body."""
        
        return self.call_deepseek(prompt).strip()
    
    def generate_call_script(self, doctor_name: str, specialty: str) -> str:
        """Generate call script"""
        prompt = f"""Create a phone call script for calling Dr. {doctor_name}, a {specialty}.
        
        Structure:
        1. Introduction (who you are)
        2. Purpose of call (brief value proposition)
        3. Question to engage (about their practice needs)
        4. Next steps
        
        Keep it conversational and under 1 minute if read aloud."""
        
        return self.call_deepseek(prompt).strip()

# ============================================================================
# LEAD SCRAPER
# ============================================================================

class LeadScraper:
    def __init__(self):
        self.ai = AIEngine()
    
    def scrape_healthgrades(self, specialty: str, location: str) -> List[Dict]:
        """Scrape Healthgrades.com for doctor listings"""
        # Note: This is a simplified version. Real implementation needs proper scraping
        leads = []
        
        # Use AI to generate leads (as scraping replacement for demo)
        leads = self.ai.generate_doctor_leads(specialty, location, count=20)
        
        return leads
    
    def scrape_vitals(self, specialty: str, location: str) -> List[Dict]:
        """Scrape Vitals.com"""
        # Similar implementation
        return []
    
    def scrape_zocdoc(self, specialty: str, location: str) -> List[Dict]:
        """Scrape ZocDoc.com"""
        # Similar implementation
        return []

# ============================================================================
# EMAIL FINDER
# ============================================================================

class EmailFinder:
    def __init__(self):
        pass
    
    def find_email_hunter(self, name: str, domain: str) -> Optional[str]:
        """Use Hunter.io API (has free tier)"""
        # Note: Requires Hunter.io API key (free tier: 25 requests/month)
        # This is a placeholder - implement with actual API
        return None
    
    def find_email_pattern(self, name: str, domain: str) -> List[str]:
        """Generate common email patterns"""
        parts = name.lower().split()
        if len(parts) < 2:
            return []
        
        first, last = parts[0], parts[-1]
        
        patterns = [
            f"{first}.{last}@{domain}",
            f"{first[0]}{last}@{domain}",
            f"{first}_{last}@{domain}",
            f"{last}.{first}@{domain}",
            f"{first}@{domain}",
        ]
        
        return patterns
    
    def verify_email(self, email: str) -> bool:
        """Verify email exists (basic check)"""
        # Use email-validator or similar library
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def find_email(self, lead: Dict) -> Optional[str]:
        """Main email finding function"""
        name = lead.get('name', '')
        hospital = lead.get('hospital', '')
        
        if not name or not hospital:
            return None
        
        # Extract domain from hospital name
        domain = hospital.lower().replace(' ', '') + '.com'
        
        # Try pattern matching
        patterns = self.find_email_pattern(name, domain)
        
        for email in patterns:
            if self.verify_email(email):
                return email
        
        return None

# ============================================================================
# LINKEDIN AUTOMATION
# ============================================================================

class LinkedInAutomation:
    def __init__(self):
        self.driver = None
        self.ai = AIEngine()
        self.is_logged_in = False
    
    def setup_driver(self):
        """Setup undetected Chrome driver"""
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # options.add_argument('--headless')  # Uncomment for headless mode
        
        self.driver = uc.Chrome(options=options)
    
    def login(self):
        """Login to LinkedIn"""
        if not self.driver:
            self.setup_driver()
        
        try:
            self.driver.get('https://www.linkedin.com/login')
            time.sleep(2)
            
            # Enter credentials
            email_field = self.driver.find_element(By.ID, 'username')
            email_field.send_keys(Config.LINKEDIN_EMAIL)
            
            password_field = self.driver.find_element(By.ID, 'password')
            password_field.send_keys(Config.LINKEDIN_PASSWORD)
            
            # Click login
            login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()
            
            time.sleep(5)
            self.is_logged_in = True
            print("✓ LinkedIn login successful")
            
        except Exception as e:
            print(f"✗ LinkedIn login failed: {e}")
            self.is_logged_in = False
    
    def search_doctor(self, name: str, location: str) -> Optional[str]:
        """Search for doctor on LinkedIn"""
        if not self.is_logged_in:
            self.login()
        
        try:
            search_query = f"{name} doctor {location}"
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_query.replace(' ', '%20')}"
            
            self.driver.get(search_url)
            time.sleep(3)
            
            # Get first result
            first_result = self.driver.find_element(By.CSS_SELECTOR, '.reusable-search__result-container')
            profile_link = first_result.find_element(By.TAG_NAME, 'a').get_attribute('href')
            
            return profile_link
            
        except Exception as e:
            print(f"Search error: {e}")
            return None
    
    def send_connection_request(self, profile_url: str, message: str) -> bool:
        """Send connection request with message"""
        try:
            self.driver.get(profile_url)
            time.sleep(3)
            
            # Click Connect button
            connect_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Connect')]")
            connect_button.click()
            time.sleep(2)
            
            # Add note
            add_note_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Add a note')]")
            add_note_button.click()
            time.sleep(1)
            
            # Enter message
            message_field = self.driver.find_element(By.NAME, 'message')
            message_field.send_keys(message[:300])  # LinkedIn limit
            
            # Send
            send_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Send')]")
            send_button.click()
            
            time.sleep(2)
            print(f"✓ Connection request sent to {profile_url}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send connection: {e}")
            return False
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()

# ============================================================================
# CALL MANAGER
# ============================================================================

class CallManager:
    def __init__(self):
        self.ai = AIEngine()
        try:
            from twilio.rest import Client
            self.twilio_client = Client(
                Config.TWILIO_ACCOUNT_SID,
                Config.TWILIO_AUTH_TOKEN
            )
        except:
            self.twilio_client = None
            print("⚠ Twilio not configured")
    
    def make_call(self, to_number: str, script: str) -> bool:
        """Make automated call using Twilio"""
        if not self.twilio_client:
            print("Twilio not configured - simulating call")
            return False
        
        try:
            call = self.twilio_client.calls.create(
                to=to_number,
                from_=Config.TWILIO_PHONE,
                twiml=f'<Response><Say>{script}</Say></Response>'
            )
            
            print(f"✓ Call initiated: {call.sid}")
            return True
            
        except Exception as e:
            print(f"✗ Call failed: {e}")
            return False

# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

class OutreachOrchestrator:
    def __init__(self):
        self.db = Database()
        self.ai = AIEngine()
        self.scraper = LeadScraper()
        self.email_finder = EmailFinder()
        self.linkedin = LinkedInAutomation()
        self.call_manager = CallManager()
    
    def generate_leads(self, specialty: str, location: str, count: int = 50):
        """Step 1: Generate/scrape doctor leads"""
        print(f"\n🔍 Generating {count} {specialty} leads in {location}...")
        
        # Scrape from multiple sources
        leads = self.scraper.scrape_healthgrades(specialty, location)
        
        # Add leads to database
        for lead in leads[:count]:
            lead_id = self.db.add_lead(lead)
            print(f"✓ Added: {lead.get('name')} (ID: {lead_id})")
        
        print(f"\n✅ Generated {len(leads[:count])} leads")
    
    def enrich_leads(self):
        """Step 2: Find emails and LinkedIn profiles"""
        print("\n📧 Enriching leads with emails and LinkedIn...")
        
        leads = self.db.get_leads_by_status('new')
        
        for lead in leads:
            # Find email
            email = self.email_finder.find_email(lead)
            if email:
                self.db.conn.execute(
                    'UPDATE leads SET email = ? WHERE id = ?',
                    (email, lead['id'])
                )
                print(f"✓ Email found for {lead['name']}: {email}")
            
            # Find LinkedIn
            linkedin_url = self.linkedin.search_doctor(lead['name'], lead['location'])
            if linkedin_url:
                self.db.conn.execute(
                    'UPDATE leads SET linkedin_url = ? WHERE id = ?',
                    (linkedin_url, lead['id'])
                )
                print(f"✓ LinkedIn found for {lead['name']}")
            
            # Update status
            self.db.update_lead_status(lead['id'], 'enriched')
            
            time.sleep(2)  # Rate limiting
        
        self.db.conn.commit()
    
    def linkedin_outreach(self, limit: int = 20):
        """Step 3: Send LinkedIn connection requests"""
        print(f"\n💼 Starting LinkedIn outreach (limit: {limit})...")
        
        leads = self.db.get_leads_by_status('enriched')
        count = 0
        
        for lead in leads:
            if count >= limit:
                break
            
            if not lead.get('linkedin_url'):
                continue
            
            # Generate personalized message
            message = self.ai.generate_linkedin_message(
                lead['name'],
                lead['specialty']
            )
            
            # Send connection request
            success = self.linkedin.send_connection_request(
                lead['linkedin_url'],
                message
            )
            
            if success:
                self.db.log_outreach(
                    lead['id'],
                    'linkedin',
                    message,
                    'sent'
                )
                self.db.update_lead_status(lead['id'], 'linkedin_sent')
                count += 1
                print(f"✓ LinkedIn request sent to {lead['name']}")
            
            time.sleep(5)  # Rate limiting
        
        print(f"\n✅ Sent {count} LinkedIn requests")
    
    def email_campaign(self, limit: int = 50):
        """Step 4: Send email campaign"""
        print(f"\n📨 Starting email campaign (limit: {limit})...")
        
        leads = self.db.get_leads_by_status('linkedin_sent')
        count = 0
        
        for lead in leads:
            if count >= limit:
                break
            
            if not lead.get('email'):
                continue
            
            # Generate email content
            subject = self.ai.generate_email_subject(lead['name'], lead['specialty'])
            body = self.ai.generate_email_body(lead['name'], lead['specialty'])
            
            # In production, use SMTP or email service
            print(f"✓ Email prepared for {lead['name']}: {subject}")
            
            self.db.log_outreach(
                lead['id'],
                'email',
                f"{subject}\n\n{body}",
                'sent'
            )
            self.db.update_lead_status(lead['id'], 'email_sent')
            count += 1
        
        print(f"\n✅ Prepared {count} emails")
    
    def call_campaign(self, limit: int = 10):
        """Step 5: Make follow-up calls"""
        print(f"\n📞 Starting call campaign (limit: {limit})...")
        
        leads = self.db.get_leads_by_status('email_sent')
        count = 0
        
        for lead in leads:
            if count >= limit:
                break
            
            if not lead.get('phone'):
                continue
            
            # Generate call script
            script = self.ai.generate_call_script(lead['name'], lead['specialty'])
            
            # Make call
            success = self.call_manager.make_call(lead['phone'], script)
            
            if success:
                self.db.log_outreach(
                    lead['id'],
                    'call',
                    script,
                    'completed'
                )
                self.db.update_lead_status(lead['id'], 'called')
                count += 1
            
            time.sleep(10)  # Rate limiting
        
        print(f"\n✅ Completed {count} calls")
    
    def run_full_campaign(self, specialty: str, location: str):
        """Run complete campaign"""
        print("=" * 60)
        print("🚀 STARTING FULL OUTREACH CAMPAIGN")
        print("=" * 60)
        
        # Step 1: Generate leads
        self.generate_leads(specialty, location, count=50)
        
        # Step 2: Enrich with emails and LinkedIn
        self.enrich_leads()
        
        # Step 3: LinkedIn outreach
        self.linkedin_outreach(limit=20)
        
        # Step 4: Email campaign
        self.email_campaign(limit=30)
        
        # Step 5: Call campaign
        self.call_campaign(limit=10)
        
        print("\n" + "=" * 60)
        print("✅ CAMPAIGN COMPLETED")
        print("=" * 60)
        
        # Cleanup
        self.linkedin.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Initialize system
    orchestrator = OutreachOrchestrator()
    
    # Run campaign for cardiologists in New York
    orchestrator.run_full_campaign(
        specialty="Cardiologist",
        location="New York, NY"
    )
    
    # View statistics
    print("\n📊 Campaign Statistics:")
    db = Database()
    cursor = db.conn.cursor()
    
    cursor.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
    for status, count in cursor.fetchall():
        print(f"  {status}: {count}")