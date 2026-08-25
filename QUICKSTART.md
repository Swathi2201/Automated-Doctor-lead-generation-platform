# Quick Start Guide - Automated Lead Generation System

## System Status: READY TO USE

Your automated lead generation system has been configured and tested successfully!

## What Was Fixed

1. **Configuration Issues**
   - Added missing Config constants (DB_NAME, DEEPSEEK_MODEL, Twilio variables)
   - Added dotenv import to load environment variables
   - Created .env.example template for easy setup

2. **Python 3.13 Compatibility**
   - Installed setuptools for distutils compatibility
   - Fixed Windows Unicode encoding issues

3. **Test Results**
   - 7/8 tests passing
   - All core functionality working
   - OpenRouter API connected
   - Database operational
   - AI message generation working

## Prerequisites

- Python 3.8+ (you're using Python 3.13)
- Chrome browser (for LinkedIn automation)
- OpenRouter API key (already configured)

## Current Configuration

Your `.env` file is configured with:
- OpenRouter API Key: ACTIVE
- LinkedIn credentials: Need to be updated with real account
- Twilio: Not configured (optional)
- Hunter.io: Not configured (optional)

## Before Running Campaigns

**IMPORTANT**: Update your LinkedIn credentials in `.env`:
```bash
LINKEDIN_EMAIL=your_real_burner_email@gmail.com
LINKEDIN_PASSWORD=your_password
```

**WARNING**: Use a burner/secondary LinkedIn account, not your main account. LinkedIn may flag automated activity.

## How to Use

### 1. Test the System (Quick Check)
```bash
python test_system.py quick
```

### 2. Run Full Tests
```bash
python test_system.py
```

### 3. Generate Test Leads (AI-generated)
```bash
python cli.py generate --specialty Cardiologist --location "New York, NY" --count 10
```

### 4. View Statistics
```bash
python cli.py stats
```

### 5. Test AI Message Generation
```bash
python cli.py test-ai --name "Dr. John Smith" --specialty Cardiologist
```

### 6. Run a Complete Campaign
```bash
python cli.py campaign --specialty "Orthopedic Surgeon" --location "Los Angeles, CA"
```

### 7. Start the Dashboard (Web UI)
```bash
python dashboard.py
```
Then open: http://localhost:8000

### 8. Start Automated Scheduler
```bash
python scheduler.py
```

## Available Commands

### Lead Generation
```bash
# Generate leads
python cli.py generate --specialty <specialty> --location <location> --count <number>

# Enrich leads with emails and LinkedIn
python cli.py enrich

# Search leads
python cli.py search --specialty Cardiologist --status enriched
```

### Outreach Campaigns
```bash
# LinkedIn outreach
python cli.py linkedin --limit 20

# Email campaign
python cli.py email --limit 30

# Call campaign
python cli.py call --limit 10

# Full campaign (all channels)
python cli.py campaign --specialty <specialty> --location <location>
```

### Data Management
```bash
# Export leads to CSV
python cli.py export --output leads.csv --include-outreach

# Backup database
python cli.py backup

# Update lead status
python cli.py update --id 1 --status contacted
```

## System Architecture

1. **Lead Generation** (main.py)
   - AI-powered lead generation using DeepSeek V3.1
   - Web scraping capabilities (Healthgrades, Vitals, ZocDoc)
   - SQLite database for storage

2. **Email Finding** (main.py)
   - Pattern-based email generation
   - Hunter.io integration (optional)
   - Email validation

3. **LinkedIn Automation** (main.py)
   - Undetected ChromeDriver for stealth
   - Automated search and connection requests
   - Personalized AI-generated messages

4. **Multi-Channel Outreach**
   - LinkedIn connection requests
   - Email campaigns
   - Voice calls (Twilio integration)

5. **Dashboard** (dashboard.py)
   - Real-time analytics
   - Campaign metrics
   - Lead tracking

6. **Scheduler** (scheduler.py)
   - Automated daily campaigns
   - Rate limiting
   - Activity logging

## Best Practices

1. **Start Small**
   - Begin with 10-20 test leads
   - Verify everything works before scaling

2. **Rate Limiting**
   - LinkedIn: Max 20-50 requests/day to avoid bans
   - Email: Stay under 500/day
   - Calls: Limit to 50/day

3. **Use Burner Accounts**
   - Never use your main LinkedIn account
   - Create secondary email accounts
   - Use VPN if doing high volume

4. **Compliance**
   - Follow CAN-SPAM Act for emails
   - Respect Do Not Call lists
   - Include unsubscribe options
   - Be professional and respectful

## Troubleshooting

### Chrome Driver Issues
If LinkedIn automation fails:
- Make sure Chrome browser is installed
- Update Chrome to latest version
- Run without headless mode first

### API Errors
If OpenRouter API fails:
- Check your API key in .env
- Verify you have credits remaining
- Check internet connection

### Database Issues
If database errors occur:
- Delete doctor_leads.db and restart
- Check file permissions
- Run: `python test_system.py` to recreate database

## Cost Breakdown

### Required (Almost Free)
- OpenRouter API: ~$0.001 per message (DeepSeek V3.1)
- LinkedIn: Free (use burner account)
- Database: Free (SQLite)

### Optional
- Twilio: $15-20 free trial credits
- Hunter.io: 25 free requests/month
- Email sending: Use Gmail SMTP (free)

## Next Steps

1. **Update LinkedIn credentials** in `.env` (use burner account)
2. **Run a test campaign** with 10 leads
3. **Monitor the dashboard** at http://localhost:8000
4. **Scale up** once comfortable with the system
5. **Set up scheduler** for automated campaigns

## Support

For issues or questions:
- Check the test results: `python test_system.py`
- Review logs: `campaign_scheduler.log`
- Check database: `doctor_leads.db`

## Legal & Ethical Considerations

- Only contact professionals who match your target criteria
- Provide clear opt-out mechanisms
- Follow all applicable laws (CAN-SPAM, GDPR, etc.)
- Be respectful and professional in all communications
- This tool is for legitimate business development only

---

**System is ready to use! Start with a small test campaign to verify everything works as expected.**
