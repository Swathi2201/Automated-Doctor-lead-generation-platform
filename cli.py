#!/usr/bin/env python3
"""
Command Line Interface for Doctor Lead Generation System
Usage: python cli.py [command] [options]
"""

import argparse
import sys
from main import OutreachOrchestrator, Database
from datetime import datetime
import json

def generate_leads(args):
    """Generate new leads"""
    print(f"\n🔍 Generating {args.count} {args.specialty} leads in {args.location}...")
    
    orchestrator = OutreachOrchestrator()
    orchestrator.generate_leads(args.specialty, args.location, args.count)
    
    print(f"✅ Successfully generated {args.count} leads")

def enrich_leads(args):
    """Find emails and LinkedIn profiles"""
    print("\n📧 Enriching leads...")
    
    orchestrator = OutreachOrchestrator()
    orchestrator.enrich_leads()
    
    print("✅ Lead enrichment completed")

def linkedin_outreach(args):
    """Send LinkedIn connection requests"""
    print(f"\n💼 Sending {args.limit} LinkedIn connection requests...")
    
    orchestrator = OutreachOrchestrator()
    orchestrator.linkedin_outreach(args.limit)
    orchestrator.linkedin.close()
    
    print(f"✅ Sent {args.limit} LinkedIn requests")

def email_campaign(args):
    """Run email campaign"""
    print(f"\n📨 Preparing {args.limit} emails...")
    
    orchestrator = OutreachOrchestrator()
    orchestrator.email_campaign(args.limit)
    
    print(f"✅ Email campaign prepared")

def call_campaign(args):
    """Run call campaign"""
    print(f"\n📞 Making {args.limit} calls...")
    
    orchestrator = OutreachOrchestrator()
    orchestrator.call_campaign(args.limit)
    
    print(f"✅ Call campaign completed")

def full_campaign(args):
    """Run complete campaign"""
    print("\n🚀 Starting full campaign...")
    
    orchestrator = OutreachOrchestrator()
    orchestrator.run_full_campaign(args.specialty, args.location)
    orchestrator.linkedin.close()
    
    print("✅ Full campaign completed")

def show_stats(args):
    """Display campaign statistics"""
    db = Database()
    cursor = db.conn.cursor()
    
    print("\n" + "=" * 60)
    print("📊 CAMPAIGN STATISTICS")
    print("=" * 60)
    
    # Total leads
    cursor.execute("SELECT COUNT(*) FROM leads")
    total = cursor.fetchone()[0]
    print(f"\n📋 Total Leads: {total}")
    
    # By status
    print("\n📈 Lead Status Breakdown:")
    cursor.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
    for status, count in cursor.fetchall():
        percentage = (count / total * 100) if total > 0 else 0
        print(f"  {status.replace('_', ' ').title():20} {count:5} ({percentage:5.1f}%)")
    
    # By specialty
    print("\n🎯 Top Specialties:")
    cursor.execute("""
        SELECT specialty, COUNT(*) as count 
        FROM leads 
        WHERE specialty IS NOT NULL
        GROUP BY specialty 
        ORDER BY count DESC 
        LIMIT 5
    """)
    for specialty, count in cursor.fetchall():
        print(f"  {specialty:30} {count:5}")
    
    # Outreach activity
    print("\n📤 Outreach Activity:")
    cursor.execute("SELECT channel, COUNT(*) FROM outreach GROUP BY channel")
    for channel, count in cursor.fetchall():
        print(f"  {channel.title():20} {count:5}")
    
    # Recent activity
    print("\n🕐 Recent Activity (Last 24h):")
    cursor.execute("""
        SELECT COUNT(*) FROM outreach 
        WHERE sent_at >= datetime('now', '-1 day')
    """)
    recent = cursor.fetchone()[0]
    print(f"  Total outreach: {recent}")
    
    print("\n" + "=" * 60)

def export_leads(args):
    """Export leads to CSV"""
    import pandas as pd
    
    db = Database()
    
    # Export leads
    df_leads = pd.read_sql_query("SELECT * FROM leads", db.conn)
    df_leads.to_csv(args.output, index=False)
    
    print(f"✅ Exported {len(df_leads)} leads to {args.output}")
    
    # Also export outreach if requested
    if args.include_outreach:
        outreach_file = args.output.replace('.csv', '_outreach.csv')
        df_outreach = pd.read_sql_query("SELECT * FROM outreach", db.conn)
        df_outreach.to_csv(outreach_file, index=False)
        print(f"✅ Exported {len(df_outreach)} outreach records to {outreach_file}")

def search_leads(args):
    """Search leads in database"""
    db = Database()
    cursor = db.conn.cursor()
    
    query = "SELECT * FROM leads WHERE 1=1"
    params = []
    
    if args.name:
        query += " AND name LIKE ?"
        params.append(f"%{args.name}%")
    
    if args.specialty:
        query += " AND specialty LIKE ?"
        params.append(f"%{args.specialty}%")
    
    if args.location:
        query += " AND location LIKE ?"
        params.append(f"%{args.location}%")
    
    if args.status:
        query += " AND status = ?"
        params.append(args.status)
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    print(f"\n🔍 Found {len(results)} matching leads:")
    print("-" * 80)
    
    for row in results[:args.limit]:
        print(f"ID: {row[0]}")
        print(f"Name: {row[1]}")
        print(f"Specialty: {row[2]}")
        print(f"Location: {row[3]}")
        print(f"Email: {row[6]}")
        print(f"Status: {row[8]}")
        print("-" * 80)

def update_lead_status(args):
    """Update lead status"""
    db = Database()
    db.update_lead_status(args.id, args.status)
    
    print(f"✅ Updated lead {args.id} status to '{args.status}'")

def test_ai(args):
    """Test AI message generation"""
    from main import AIEngine
    
    ai = AIEngine()
    
    print("\n🤖 Testing AI Message Generation...")
    print("-" * 60)
    
    # Test LinkedIn message
    print("\n💼 LinkedIn Message:")
    linkedin_msg = ai.generate_linkedin_message(args.name, args.specialty)
    print(linkedin_msg)
    
    # Test email subject
    print("\n📧 Email Subject:")
    email_subject = ai.generate_email_subject(args.name, args.specialty)
    print(email_subject)
    
    # Test email body
    print("\n📝 Email Body:")
    email_body = ai.generate_email_body(args.name, args.specialty)
    print(email_body)
    
    # Test call script
    print("\n📞 Call Script:")
    call_script = ai.generate_call_script(args.name, args.specialty)
    print(call_script)
    
    print("\n" + "-" * 60)

def backup_database(args):
    """Backup database"""
    import shutil
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"doctor_leads_backup_{timestamp}.db"
    
    shutil.copy('doctor_leads.db', backup_file)
    print(f"✅ Database backed up to {backup_file}")

def main():
    parser = argparse.ArgumentParser(
        description='Doctor Lead Generation System CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate leads
  python cli.py generate --specialty Cardiologist --location "New York, NY" --count 50
  
  # Enrich leads with emails
  python cli.py enrich
  
  # LinkedIn outreach
  python cli.py linkedin --limit 20
  
  # Run full campaign
  python cli.py campaign --specialty "Orthopedic Surgeon" --location "Los Angeles, CA"
  
  # Show statistics
  python cli.py stats
  
  # Export leads
  python cli.py export --output leads.csv
  
  # Search leads
  python cli.py search --specialty Cardiologist --status enriched
  
  # Test AI
  python cli.py test-ai --name "Dr. John Smith" --specialty Cardiologist
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate leads
    parser_generate = subparsers.add_parser('generate', help='Generate new leads')
    parser_generate.add_argument('--specialty', required=True, help='Medical specialty')
    parser_generate.add_argument('--location', required=True, help='Location')
    parser_generate.add_argument('--count', type=int, default=50, help='Number of leads')
    parser_generate.set_defaults(func=generate_leads)
    
    # Enrich leads
    parser_enrich = subparsers.add_parser('enrich', help='Find emails and LinkedIn')
    parser_enrich.set_defaults(func=enrich_leads)
    
    # LinkedIn outreach
    parser_linkedin = subparsers.add_parser('linkedin', help='Send LinkedIn requests')
    parser_linkedin.add_argument('--limit', type=int, default=20, help='Number of requests')
    parser_linkedin.set_defaults(func=linkedin_outreach)
    
    # Email campaign
    parser_email = subparsers.add_parser('email', help='Run email campaign')
    parser_email.add_argument('--limit', type=int, default=30, help='Number of emails')
    parser_email.set_defaults(func=email_campaign)
    
    # Call campaign
    parser_call = subparsers.add_parser('call', help='Run call campaign')
    parser_call.add_argument('--limit', type=int, default=10, help='Number of calls')
    parser_call.set_defaults(func=call_campaign)
    
    # Full campaign
    parser_campaign = subparsers.add_parser('campaign', help='Run complete campaign')
    parser_campaign.add_argument('--specialty', required=True, help='Medical specialty')
    parser_campaign.add_argument('--location', required=True, help='Location')
    parser_campaign.set_defaults(func=full_campaign)
    
    # Statistics
    parser_stats = subparsers.add_parser('stats', help='Show campaign statistics')
    parser_stats.set_defaults(func=show_stats)
    
    # Export
    parser_export = subparsers.add_parser('export', help='Export leads to CSV')
    parser_export.add_argument('--output', default='leads_export.csv', help='Output filename')
    parser_export.add_argument('--include-outreach', action='store_true', help='Also export outreach data')
    parser_export.set_defaults(func=export_leads)
    
    # Search
    parser_search = subparsers.add_parser('search', help='Search leads')
    parser_search.add_argument('--name', help='Search by name')
    parser_search.add_argument('--specialty', help='Search by specialty')
    parser_search.add_argument('--location', help='Search by location')
    parser_search.add_argument('--status', help='Search by status')
    parser_search.add_argument('--limit', type=int, default=10, help='Max results')
    parser_search.set_defaults(func=search_leads)
    
    # Update status
    parser_update = subparsers.add_parser('update', help='Update lead status')
    parser_update.add_argument('--id', type=int, required=True, help='Lead ID')
    parser_update.add_argument('--status', required=True, help='New status')
    parser_update.set_defaults(func=update_lead_status)
    
    # Test AI
    parser_test = subparsers.add_parser('test-ai', help='Test AI message generation')
    parser_test.add_argument('--name', required=True, help='Doctor name')
    parser_test.add_argument('--specialty', required=True, help='Specialty')
    parser_test.set_defaults(func=test_ai)
    
    # Backup
    parser_backup = subparsers.add_parser('backup', help='Backup database')
    parser_backup.set_defaults(func=backup_database)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()