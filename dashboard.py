"""
Analytics Dashboard for Doctor Lead Generation System
Run with: python dashboard.py
Access at: http://localhost:8000
"""

import sqlite3
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime, timedelta

app = FastAPI(title="Doctor Lead Gen Dashboard")

class DashboardData:
    def __init__(self):
        self.conn = sqlite3.connect('doctor_leads.db', check_same_thread=False)
    
    def get_total_leads(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM leads")
        return cursor.fetchone()[0]
    
    def get_leads_by_status(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
        return dict(cursor.fetchall())
    
    def get_recent_outreach(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT l.name, o.channel, o.status, o.sent_at
            FROM outreach o
            JOIN leads l ON o.lead_id = l.id
            ORDER BY o.sent_at DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()
    
    def get_conversion_rates(self):
        cursor = self.conn.cursor()
        
        # Calculate conversion rates
        total = self.get_total_leads()
        if total == 0:
            return {}
        
        cursor.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
        status_counts = dict(cursor.fetchall())
        
        return {
            'email_rate': (status_counts.get('email_sent', 0) / total) * 100,
            'linkedin_rate': (status_counts.get('linkedin_sent', 0) / total) * 100,
            'call_rate': (status_counts.get('called', 0) / total) * 100
        }
    
    def get_top_specialties(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT specialty, COUNT(*) as count 
            FROM leads 
            GROUP BY specialty 
            ORDER BY count DESC 
            LIMIT 5
        """)
        return cursor.fetchall()
    
    def get_daily_activity(self, days=7):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DATE(sent_at) as date, COUNT(*) as count
            FROM outreach
            WHERE sent_at >= date('now', '-' || ? || ' days')
            GROUP BY DATE(sent_at)
            ORDER BY date DESC
        """, (days,))
        return cursor.fetchall()

dashboard_data = DashboardData()

@app.get("/", response_class=HTMLResponse)
async def home():
    """Main dashboard page"""
    
    # Get statistics
    total_leads = dashboard_data.get_total_leads()
    status_breakdown = dashboard_data.get_leads_by_status()
    conversion_rates = dashboard_data.get_conversion_rates()
    recent_outreach = dashboard_data.get_recent_outreach(10)
    top_specialties = dashboard_data.get_top_specialties()
    daily_activity = dashboard_data.get_daily_activity(7)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Doctor Lead Gen Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
            }}
            
            .header {{
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }}
            
            h1 {{
                color: #2d3748;
                font-size: 32px;
                margin-bottom: 10px;
            }}
            
            .subtitle {{
                color: #718096;
                font-size: 16px;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .stat-card {{
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }}
            
            .stat-card:hover {{
                transform: translateY(-5px);
            }}
            
            .stat-label {{
                color: #718096;
                font-size: 14px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 10px;
            }}
            
            .stat-value {{
                color: #2d3748;
                font-size: 36px;
                font-weight: bold;
            }}
            
            .stat-icon {{
                font-size: 48px;
                float: right;
                opacity: 0.3;
            }}
            
            .content-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
                gap: 20px;
            }}
            
            .card {{
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            }}
            
            .card-title {{
                color: #2d3748;
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid #e2e8f0;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            
            th {{
                text-align: left;
                padding: 12px;
                color: #718096;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-weight: 600;
            }}
            
            td {{
                padding: 12px;
                color: #2d3748;
                border-top: 1px solid #e2e8f0;
            }}
            
            .status-badge {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
            }}
            
            .status-new {{ background: #bee3f8; color: #2c5282; }}
            .status-enriched {{ background: #c6f6d5; color: #276749; }}
            .status-linkedin-sent {{ background: #feebc8; color: #7c2d12; }}
            .status-email-sent {{ background: #e9d8fd; color: #553c9a; }}
            .status-called {{ background: #fed7d7; color: #742a2a; }}
            
            .progress-bar {{
                width: 100%;
                height: 8px;
                background: #e2e8f0;
                border-radius: 10px;
                overflow: hidden;
                margin: 10px 0;
            }}
            
            .progress-fill {{
                height: 100%;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                transition: width 0.3s ease;
            }}
            
            .channel-icon {{
                font-size: 20px;
                margin-right: 8px;
            }}
            
            @media (max-width: 768px) {{
                .content-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 Doctor Lead Generation Dashboard</h1>
                <p class="subtitle">Real-time analytics for your outreach campaigns</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">👨‍⚕️</div>
                    <div class="stat-label">Total Leads</div>
                    <div class="stat-value">{total_leads}</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">📧</div>
                    <div class="stat-label">Emails Sent</div>
                    <div class="stat-value">{status_breakdown.get('email_sent', 0)}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {conversion_rates.get('email_rate', 0)}%"></div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">💼</div>
                    <div class="stat-label">LinkedIn Requests</div>
                    <div class="stat-value">{status_breakdown.get('linkedin_sent', 0)}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {conversion_rates.get('linkedin_rate', 0)}%"></div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">📞</div>
                    <div class="stat-label">Calls Made</div>
                    <div class="stat-value">{status_breakdown.get('called', 0)}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {conversion_rates.get('call_rate', 0)}%"></div>
                    </div>
                </div>
            </div>
            
            <div class="content-grid">
                <div class="card">
                    <h2 class="card-title">📊 Lead Status Breakdown</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Status</th>
                                <th>Count</th>
                                <th>Percentage</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    for status, count in status_breakdown.items():
        percentage = (count / total_leads * 100) if total_leads > 0 else 0
        html += f"""
                            <tr>
                                <td><span class="status-badge status-{status}">{status.replace('_', ' ').title()}</span></td>
                                <td>{count}</td>
                                <td>{percentage:.1f}%</td>
                            </tr>
        """
    
    html += """
                        </tbody>
                    </table>
                </div>
                
                <div class="card">
                    <h2 class="card-title">🎯 Top Specialties</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Specialty</th>
                                <th>Lead Count</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    for specialty, count in top_specialties:
        html += f"""
                            <tr>
                                <td>{specialty if specialty else 'Not specified'}</td>
                                <td><strong>{count}</strong></td>
                            </tr>
        """
    
    html += """
                        </tbody>
                    </table>
                </div>
                
                <div class="card" style="grid-column: 1 / -1;">
                    <h2 class="card-title">🔔 Recent Outreach Activity</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Doctor Name</th>
                                <th>Channel</th>
                                <th>Status</th>
                                <th>Time</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    channel_icons = {
        'email': '📧',
        'linkedin': '💼',
        'call': '📞'
    }
    
    for name, channel, status, sent_at in recent_outreach:
        icon = channel_icons.get(channel, '📤')
        html += f"""
                            <tr>
                                <td>{name}</td>
                                <td><span class="channel-icon">{icon}</span>{channel.title()}</td>
                                <td><span class="status-badge status-{status}">{status.title()}</span></td>
                                <td>{sent_at}</td>
                            </tr>
        """
    
    html += """
                        </tbody>
                    </table>
                </div>
                
                <div class="card" style="grid-column: 1 / -1;">
                    <h2 class="card-title">📈 Daily Activity (Last 7 Days)</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Outreach Activities</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    for date, count in daily_activity:
        html += f"""
                            <tr>
                                <td>{date}</td>
                                <td><strong>{count}</strong> activities</td>
                            </tr>
        """
    
    html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <script>
            // Auto-refresh every 30 seconds
            setTimeout(() => location.reload(), 30000);
        </script>
    </body>
    </html>
    """
    
    return html

@app.get("/api/stats")
async def get_stats():
    """API endpoint for statistics"""
    return {
        "total_leads": dashboard_data.get_total_leads(),
        "status_breakdown": dashboard_data.get_leads_by_status(),
        "conversion_rates": dashboard_data.get_conversion_rates(),
        "top_specialties": dashboard_data.get_top_specialties()
    }

if __name__ == "__main__":
    print("🚀 Starting Dashboard Server...")
    print("📊 Access dashboard at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)