# 🏥 AI-Powered Doctor Lead Generation System

> Automate your medical marketing outreach with AI-powered lead generation, email finding, LinkedIn automation, and multi-channel campaigns.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
# Clone or download project
git clone <your-repo-url>
cd doctor-lead-gen

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

Add your **OpenRouter API key** (required):
- Sign up: https://openrouter.ai/
- Get free credits for DeepSeek V3.1

### 3. Run Your First Campaign

```bash
# Generate 10 test leads
python cli.py generate --specialty Cardiologist --location "New York, NY" --count 10

# Enrich with emails
python cli.py enrich

# View statistics
python cli.py stats
```

## 📊 Features

| Feature | Status | Description |
|---------|--------|-------------|
| 🤖 AI Lead Generation | ✅ | Uses DeepSeek V3.1 to generate qualified leads |
| 📧 Email Finding | ✅ | Pattern matching + Hunter.io integration |
| 💼 LinkedIn Automation | ✅ | Automated connection requests + messaging |
| 📨 Email Campaigns | ✅ | AI-generated personalized emails |
| 📞 Call Campaigns | ✅ | Twilio voice automation |
| 📊 Analytics Dashboard | ✅ | Real-time metrics and insights |
| ⏰ Scheduler | ✅ | Automated daily campaigns |
| 💾 CRM Database | ✅ | SQLite with full tracking |

## 🎯 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     LEAD GENERATION                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐  │
│  │ AI Model │→ │ Scraper  │→ │ Database (SQLite)        │  │
│  └──────────┘  └──────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐