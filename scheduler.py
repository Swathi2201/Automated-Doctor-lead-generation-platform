"""
Automated Scheduler for Doctor Lead Generation
Runs campaigns automatically at scheduled times
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
from main import OutreachOrchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('campaign_scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class CampaignScheduler:
    def __init__(self):
        self.orchestrator = OutreachOrchestrator()
        self.scheduler = BlockingScheduler()
    
    def daily_lead_generation(self):
        """Generate new leads every day at 8 AM"""
        logger.info("🔍 Starting daily lead generation...")
        try:
            self.orchestrator.generate_leads(
                specialty="Cardiologist",
                location="New York, NY",
                count=50
            )
            logger.info("✅ Daily lead generation completed")
        except Exception as e:
            logger.error(f"❌ Lead generation failed: {e}")
    
    def morning_enrichment(self):
        """Enrich leads every morning at 9 AM"""
        logger.info("📧 Starting morning lead enrichment...")
        try:
            self.orchestrator.enrich_leads()
            logger.info("✅ Lead enrichment completed")
        except Exception as e:
            logger.error(f"❌ Lead enrichment failed: {e}")
    
    def linkedin_outreach_batch(self):
        """Send LinkedIn requests - spread throughout the day"""
        logger.info("💼 Starting LinkedIn outreach batch...")
        try:
            self.orchestrator.linkedin_outreach(limit=20)
            logger.info("✅ LinkedIn outreach completed")
        except Exception as e:
            logger.error(f"❌ LinkedIn outreach failed: {e}")
    
    def email_campaign_batch(self):
        """Send email batch - spread throughout the day"""
        logger.info("📨 Starting email campaign batch...")
        try:
            self.orchestrator.email_campaign(limit=30)
            logger.info("✅ Email campaign completed")
        except Exception as e:
            logger.error(f"❌ Email campaign failed: {e}")
    
    def afternoon_calls(self):
        """Make calls in the afternoon"""
        logger.info("📞 Starting afternoon call campaign...")
        try:
            self.orchestrator.call_campaign(limit=10)
            logger.info("✅ Call campaign completed")
        except Exception as e:
            logger.error(f"❌ Call campaign failed: {e}")
    
    def weekly_report(self):
        """Generate weekly performance report"""
        logger.info("📊 Generating weekly report...")
        try:
            db = self.orchestrator.db
            cursor = db.conn.cursor()
            
            # Get statistics
            cursor.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
            stats = dict(cursor.fetchall())
            
            cursor.execute("SELECT COUNT(*) FROM outreach WHERE sent_at >= date('now', '-7 days')")
            weekly_outreach = cursor.fetchone()[0]
            
            report = f"""
            ========================================
            WEEKLY PERFORMANCE REPORT
            ========================================
            Date: {datetime.now().strftime('%Y-%m-%d')}
            
            Lead Statistics:
            {'-' * 40}
            """
            
            for status, count in stats.items():
                report += f"  {status.replace('_', ' ').title()}: {count}\n"
            
            report += f"""
            {'-' * 40}
            Total Outreach (Last 7 Days): {weekly_outreach}
            ========================================
            """
            
            logger.info(report)
            
            # Optionally send email report
            # send_email_report(report)
            
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")
    
    def setup_schedule(self):
        """Setup all scheduled jobs"""
        
        # Daily lead generation at 8 AM
        self.scheduler.add_job(
            self.daily_lead_generation,
            CronTrigger(hour=8, minute=0),
            id='daily_lead_gen',
            name='Daily Lead Generation'
        )
        
        # Morning enrichment at 9 AM
        self.scheduler.add_job(
            self.morning_enrichment,
            CronTrigger(hour=9, minute=0),
            id='morning_enrichment',
            name='Morning Lead Enrichment'
        )
        
        # LinkedIn outreach - 3 times per day (10 AM, 2 PM, 5 PM)
        for hour in [10, 14, 17]:
            self.scheduler.add_job(
                self.linkedin_outreach_batch,
                CronTrigger(hour=hour, minute=0),
                id=f'linkedin_outreach_{hour}',
                name=f'LinkedIn Outreach {hour}:00'
            )
        
        # Email campaigns - 4 times per day (10:30 AM, 1 PM, 3:30 PM, 6 PM)
        for hour, minute in [(10, 30), (13, 0), (15, 30), (18, 0)]:
            self.scheduler.add_job(
                self.email_campaign_batch,
                CronTrigger(hour=hour, minute=minute),
                id=f'email_campaign_{hour}_{minute}',
                name=f'Email Campaign {hour}:{minute:02d}'
            )
        
        # Afternoon calls at 2:30 PM and 4:30 PM
        for hour, minute in [(14, 30), (16, 30)]:
            self.scheduler.add_job(
                self.afternoon_calls,
                CronTrigger(hour=hour, minute=minute),
                id=f'calls_{hour}_{minute}',
                name=f'Call Campaign {hour}:{minute:02d}'
            )
        
        # Weekly report every Monday at 9 AM
        self.scheduler.add_job(
            self.weekly_report,
            CronTrigger(day_of_week='mon', hour=9, minute=0),
            id='weekly_report',
            name='Weekly Performance Report'
        )
        
        logger.info("✅ Scheduler configured with all jobs")
        self.print_schedule()
    
    def print_schedule(self):
        """Print all scheduled jobs"""
        logger.info("\n" + "=" * 60)
        logger.info("SCHEDULED JOBS")
        logger.info("=" * 60)
        
        for job in self.scheduler.get_jobs():
            logger.info(f"  {job.name}")
            logger.info(f"    Next run: {job.next_run_time}")
            logger.info("")
    
    def start(self):
        """Start the scheduler"""
        logger.info("🚀 Starting Campaign Scheduler...")
        self.setup_schedule()
        
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("⏹️  Scheduler stopped by user")
            self.orchestrator.linkedin.close()

# ============================================================================
# MANUAL TRIGGERS (for testing)
# ============================================================================

def run_test_campaign():
    """Run a small test campaign immediately"""
    logger.info("🧪 Running test campaign...")
    
    orchestrator = OutreachOrchestrator()
    
    # Generate 10 test leads
    orchestrator.generate_leads("Cardiologist", "New York, NY", count=10)
    
    # Enrich them
    orchestrator.enrich_leads()
    
    # Try LinkedIn outreach (limit 2)
    orchestrator.linkedin_outreach(limit=2)
    
    logger.info("✅ Test campaign completed")
    orchestrator.linkedin.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run test campaign
        run_test_campaign()
    else:
        # Start scheduler
        scheduler = CampaignScheduler()
        scheduler.start()