#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Test Suite - Test all components before running campaigns
Run: python test_system.py
"""

import os
import sys
from colorama import init, Fore, Style

# Fix Windows encoding for Unicode characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

init(autoreset=True)

def print_header(text):
    print("\n" + "=" * 60)
    print(f"{Fore.CYAN}{Style.BRIGHT}{text}")
    print("=" * 60)

def print_success(text):
    print(f"{Fore.GREEN}✓ {text}")

def print_error(text):
    print(f"{Fore.RED}✗ {text}")

def print_warning(text):
    print(f"{Fore.YELLOW}⚠ {text}")

def print_info(text):
    print(f"{Fore.BLUE}ℹ {text}")

def test_imports():
    """Test if all required packages are installed"""
    print_header("Testing Python Packages")
    
    required_packages = [
        ('requests', 'requests'),
        ('selenium', 'selenium'),
        ('beautifulsoup4', 'bs4'),
        ('undetected-chromedriver', 'undetected_chromedriver'),
        ('fastapi', 'fastapi'),
        ('twilio', 'twilio'),
        ('apscheduler', 'apscheduler'),
        ('pandas', 'pandas'),
    ]
    
    all_good = True
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print_success(f"{package_name} installed")
        except ImportError:
            print_error(f"{package_name} NOT installed")
            all_good = False
    
    return all_good

def test_env_config():
    """Test environment configuration"""
    print_header("Testing Configuration")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'OPENROUTER_API_KEY': 'OpenRouter API Key (REQUIRED)',
        'LINKEDIN_EMAIL': 'LinkedIn Email (for LinkedIn automation)',
        'LINKEDIN_PASSWORD': 'LinkedIn Password (for LinkedIn automation)',
    }
    
    optional_vars = {
        'TWILIO_ACCOUNT_SID': 'Twilio Account SID (for calls)',
        'TWILIO_AUTH_TOKEN': 'Twilio Auth Token (for calls)',
        'TWILIO_PHONE': 'Twilio Phone Number (for calls)',
        'HUNTER_API_KEY': 'Hunter.io API Key (for email finding)',
    }
    
    all_required_present = True
    
    # Check required
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}":
            print_success(f"{description}")
        else:
            print_error(f"{description} - NOT SET")
            all_required_present = False
    
    # Check optional
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}":
            print_success(f"{description}")
        else:
            print_warning(f"{description} - Optional, not set")
    
    return all_required_present

def test_openrouter_api():
    """Test OpenRouter API connection"""
    print_header("Testing OpenRouter API")
    
    try:
        from main import AIEngine
        
        ai = AIEngine()
        
        # Try simple API call
        print_info("Making test API call to DeepSeek V3.1...")
        response = ai.call_deepseek("Say 'test successful' in 2 words")
        
        if response:
            print_success("OpenRouter API connection successful")
            print_info(f"Response: {response[:100]}...")
            return True
        else:
            print_error("OpenRouter API returned empty response")
            return False
            
    except Exception as e:
        print_error(f"OpenRouter API test failed: {e}")
        return False

def test_database():
    """Test database creation and operations"""
    print_header("Testing Database")
    
    try:
        from main import Database
        
        db = Database()
        
        # Test insert
        test_lead = {
            'name': 'Dr. Test',
            'specialty': 'Test Specialty',
            'location': 'Test City',
            'hospital': 'Test Hospital',
            'phone': '1234567890',
            'email': 'test@test.com',
            'linkedin_url': 'https://linkedin.com/test',
            'priority': 5
        }
        
        lead_id = db.add_lead(test_lead)
        print_success(f"Database write successful (Lead ID: {lead_id})")
        
        # Test read
        leads = db.get_leads_by_status('new')
        print_success(f"Database read successful ({len(leads)} leads)")
        
        # Test update
        db.update_lead_status(lead_id, 'test')
        print_success("Database update successful")
        
        # Clean up
        db.conn.execute('DELETE FROM leads WHERE id = ?', (lead_id,))
        db.conn.commit()
        print_success("Database cleanup successful")
        
        return True
        
    except Exception as e:
        print_error(f"Database test failed: {e}")
        return False

def test_email_finder():
    """Test email finding functionality"""
    print_header("Testing Email Finder")
    
    try:
        from main import EmailFinder
        
        finder = EmailFinder()
        
        # Test pattern generation
        patterns = finder.find_email_pattern("John Doe", "hospital.com")
        print_success(f"Generated {len(patterns)} email patterns")
        print_info(f"Sample patterns: {patterns[:3]}")
        
        # Test email verification
        valid = finder.verify_email("test@example.com")
        invalid = finder.verify_email("not-an-email")
        
        if valid and not invalid:
            print_success("Email validation working correctly")
            return True
        else:
            print_error("Email validation not working correctly")
            return False
            
    except Exception as e:
        print_error(f"Email finder test failed: {e}")
        return False

def test_chrome_driver():
    """Test Chrome driver setup"""
    print_header("Testing Chrome Driver")
    
    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.chrome.options import Options
        
        print_info("Initializing Chrome driver...")
        
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = uc.Chrome(options=options)
        
        # Test navigation
        driver.get('https://www.google.com')
        
        if "Google" in driver.title:
            print_success("Chrome driver working correctly")
            driver.quit()
            return True
        else:
            print_error("Chrome driver navigation failed")
            driver.quit()
            return False
            
    except Exception as e:
        print_error(f"Chrome driver test failed: {e}")
        print_info("Make sure Chrome browser is installed")
        return False

def test_ai_generation():
    """Test AI message generation"""
    print_header("Testing AI Message Generation")
    
    try:
        from main import AIEngine
        
        ai = AIEngine()
        
        # Test LinkedIn message
        print_info("Generating LinkedIn message...")
        linkedin_msg = ai.generate_linkedin_message("Dr. John Smith", "Cardiologist")
        
        if linkedin_msg and len(linkedin_msg) > 20:
            print_success("LinkedIn message generation successful")
            print_info(f"Sample: {linkedin_msg[:80]}...")
        else:
            print_error("LinkedIn message generation failed")
            return False
        
        # Test email subject
        print_info("Generating email subject...")
        subject = ai.generate_email_subject("Dr. John Smith", "Cardiologist")
        
        if subject and len(subject) > 5:
            print_success("Email subject generation successful")
            print_info(f"Sample: {subject}")
        else:
            print_error("Email subject generation failed")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"AI generation test failed: {e}")
        return False

def test_twilio():
    """Test Twilio configuration (optional)"""
    print_header("Testing Twilio (Optional)")
    
    try:
        from twilio.rest import Client
        
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        
        if not account_sid or not auth_token:
            print_warning("Twilio credentials not configured (optional)")
            return True  # Not a failure
        
        client = Client(account_sid, auth_token)
        
        # Test by fetching account info
        account = client.api.accounts(account_sid).fetch()
        
        print_success(f"Twilio connection successful (Account: {account.friendly_name})")
        return True
        
    except Exception as e:
        print_warning(f"Twilio test failed (optional): {e}")
        return True  # Not critical

def run_all_tests():
    """Run all tests and provide summary"""
    print("\n" + "█" * 60)
    print(f"{Fore.CYAN}{Style.BRIGHT}     DOCTOR LEAD GENERATION SYSTEM - TEST SUITE")
    print("█" * 60)
    
    tests = [
        ("Python Packages", test_imports),
        ("Environment Configuration", test_env_config),
        ("OpenRouter API", test_openrouter_api),
        ("Database Operations", test_database),
        ("Email Finder", test_email_finder),
        ("Chrome Driver", test_chrome_driver),
        ("AI Message Generation", test_ai_generation),
        ("Twilio Integration", test_twilio),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_error(f"Test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print("\n" + "=" * 60)
    print(f"{Fore.CYAN}Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}🎉 ALL TESTS PASSED! System is ready to use.")
        print(f"\n{Fore.CYAN}Next steps:")
        print("  1. Run a test campaign: python cli.py campaign --specialty Cardiologist --location 'New York, NY'")
        print("  2. Start dashboard: python dashboard.py")
        print("  3. Start scheduler: python scheduler.py")
        return True
    else:
        print(f"\n{Fore.RED}{Style.BRIGHT}⚠ SOME TESTS FAILED")
        print(f"\n{Fore.YELLOW}Please fix the issues above before running campaigns.")
        print(f"\n{Fore.CYAN}Common solutions:")
        print("  1. Install missing packages: pip install -r requirements.txt")
        print("  2. Configure API keys in .env file")
        print("  3. Check SETUP_GUIDE.md for detailed instructions")
        return False

def quick_test():
    """Run a minimal quick test"""
    print_header("Quick System Check")

    tests = [
        test_imports,
        test_env_config,
        test_database,
    ]
    
    all_passed = all(test() for test in tests)
    
    if all_passed:
        print(f"\n{Fore.GREEN}✓ Quick check passed! Run 'python test_system.py' for full tests.")
    else:
        print(f"\n{Fore.RED}✗ Quick check failed. See errors above.")
    
    return all_passed

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_test()
    else:
        success = run_all_tests()
        sys.exit(0 if success else 1)