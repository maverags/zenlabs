"""
FastAPI Backend for Spa/Salon AI Agent System
Complete version with dashboard UI, API routes, and ACTIVE AI AGENTS
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import asyncpg
import os
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel
import logging
import anthropic
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection pool
db_pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global db_pool
    
    # Startup: Create database pool
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL not set!")
        raise ValueError("DATABASE_URL environment variable required")
    
    try:
        db_pool = await asyncpg.create_pool(
            database_url,
            min_size=2,
            max_size=10
        )
        logger.info("✅ Database pool created")
    except Exception as e:
        logger.error(f"Failed to create database pool: {e}")
        raise
    
    # Check if Anthropic API key is available
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        logger.info("✅ ANTHROPIC_API_KEY found - AI agents enabled")
    else:
        logger.warning("⚠️ ANTHROPIC_API_KEY not set - AI agents will be disabled")
    
    yield
    
    # Shutdown: Close database pool
    if db_pool:
        await db_pool.close()
        logger.info("✅ Database pool closed")

# Initialize FastAPI app
app = FastAPI(
    title="Spa Agent AI API",
    description="AI-powered spa/salon management system with autonomous agents",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database connection
async def get_db():
    async with db_pool.acquire() as conn:
        yield conn

# ================================================================
# PYDANTIC MODELS
# ================================================================

class DashboardMetrics(BaseModel):
    today_appointments: int
    today_revenue: float
    active_staff: int
    low_stock_items: int
    at_risk_customers: int

class AgentAnalysisRequest(BaseModel):
    agent_type: str = "churn_detection"  # churn_detection, scheduler, inventory, all
    
class CustomerInsight(BaseModel):
    customer_id: str
    customer_name: str
    days_since_visit: int
    total_ltv: float
    churn_probability: float
    recommendation: str
    expected_recovery: float
    best_contact_time: str
    preferred_channel: str

class AgentAnalysisResponse(BaseModel):
    agent_type: str
    status: str
    total_analyzed: int
    insights: List[Dict[str, Any]]
    summary: str
    total_opportunity: float
    confidence: float
    timestamp: datetime

# ================================================================
# DASHBOARD UI - ROOT ENDPOINT
# ================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main dashboard with AI agent insights"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Spa/Salon AI Agent System</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                color: white;
                margin-bottom: 40px;
            }
            .header h1 {
                font-size: 48px;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }
            .header p {
                font-size: 20px;
                opacity: 0.9;
            }
            .cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .card {
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                transition: transform 0.3s ease;
                cursor: pointer;
            }
            .card:hover {
                transform: translateY(-5px);
            }
            .card h3 {
                color: #667eea;
                margin-bottom: 15px;
                font-size: 24px;
            }
            .card p {
                color: #666;
                line-height: 1.6;
                margin-bottom: 20px;
            }
            .card .value {
                font-size: 36px;
                font-weight: bold;
                color: #667eea;
                margin-bottom: 10px;
            }
            .btn {
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 600;
                transition: background 0.3s ease;
                border: none;
                cursor: pointer;
            }
            .btn:hover {
                background: #5568d3;
            }
            .btn-success {
                background: #28a745;
            }
            .btn-success:hover {
                background: #218838;
            }
            .status {
                background: white;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
            }
            .status-item {
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #eee;
            }
            .status-item:last-child {
                border-bottom: none;
            }
            .status-label {
                font-weight: 600;
                color: #333;
            }
            .status-value {
                color: #667eea;
                font-weight: 600;
            }
            .ai-insights {
                background: white;
                border-radius: 12px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .ai-insights h2 {
                color: #667eea;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .insight-card {
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 20px;
                margin-bottom: 15px;
                border-radius: 8px;
            }
            .insight-card.warning {
                border-left-color: #ffc107;
                background: #fff9e6;
            }
            .insight-card.success {
                border-left-color: #28a745;
                background: #e6f9e6;
            }
            .insight-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .insight-title {
                font-size: 18px;
                font-weight: bold;
                color: #333;
            }
            .insight-value {
                font-size: 24px;
                font-weight: bold;
                color: #667eea;
            }
            .insight-detail {
                color: #666;
                margin-bottom: 15px;
                line-height: 1.6;
            }
            .loading {
                text-align: center;
                padding: 40px;
                color: #999;
            }
            .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .metric-card {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                text-align: center;
            }
            .metric-value {
                font-size: 48px;
                font-weight: bold;
                color: #667eea;
                margin: 10px 0;
            }
            .metric-label {
                font-size: 16px;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .footer {
                text-align: center;
                color: white;
                margin-top: 40px;
                opacity: 0.8;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Spa Agent AI System</h1>
                <p>Autonomous AI Agents Analyzing Your Business in Real-Time</p>
            </div>

            <div class="status" id="system-status">
                <h3 style="margin-bottom: 15px; color: #667eea;">System Status</h3>
                <div class="status-item">
                    <span class="status-label">API Status:</span>
                    <span class="status-value" id="api-status">Loading...</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Database:</span>
                    <span class="status-value" id="db-status">Loading...</span>
                </div>
                <div class="status-item">
                    <span class="status-label">AI Agents:</span>
                    <span class="status-value" id="ai-status">Ready</span>
                </div>
            </div>

            <!-- AI INSIGHTS SECTION -->
            <div class="ai-insights">
                <h2>🤖 AI Agent Insights</h2>
                <div style="margin-bottom: 20px;">
                    <button class="btn btn-success" onclick="runChurnAnalysis()">🔍 Run Churn Detection Agent</button>
                    <button class="btn" onclick="runSchedulerAnalysis()">📅 Run Scheduler Agent</button>
                    <button class="btn" onclick="runInventoryAnalysis()">📦 Run Inventory Agent</button>
                </div>
                <div id="ai-insights-content">
                    <div class="loading">
                        <p>Click "Run Churn Detection Agent" to see AI-powered customer insights</p>
                    </div>
                </div>
            </div>

            <h2 style="color: white; margin: 30px 0 20px 0; text-align: center;">📊 Live Business Metrics</h2>
            
            <div class="cards" id="metrics-cards">
                <div class="metric-card">
                    <div class="metric-label">Today's Appointments</div>
                    <div class="metric-value" id="appointments">-</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Today's Revenue</div>
                    <div class="metric-value" id="revenue">$0</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Active Staff</div>
                    <div class="metric-value" id="staff">-</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">At-Risk Customers</div>
                    <div class="metric-value" id="at-risk">-</div>
                </div>
            </div>

            <h2 style="color: white; margin: 30px 0 20px 0; text-align: center;">🔧 Quick Actions</h2>

            <div class="cards">
                <div class="card" onclick="window.open('/api/services', '_blank')">
                    <h3>📋 Services</h3>
                    <p>View all 30 professional services with pricing and details.</p>
                    <div class="value">30</div>
                </div>

                <div class="card" onclick="window.open('/api/staff', '_blank')">
                    <h3>👥 Staff Members</h3>
                    <p>View staff roster, schedules, and availability.</p>
                    <div class="value">7</div>
                </div>

                <div class="card" onclick="window.open('/api/customers/at-risk', '_blank')">
                    <h3>⚠️ At-Risk Customers</h3>
                    <p>Customers who need retention campaigns.</p>
                    <div class="value" id="at-risk-count">-</div>
                </div>

                <div class="card" onclick="window.open('/docs', '_blank')">
                    <h3>📚 API Documentation</h3>
                    <p>Interactive API docs with testing capabilities.</p>
                    <a class="btn">Open Docs</a>
                </div>
            </div>

            <div class="footer">
                <p>🚀 Powered by Claude AI (Sonnet 4), FastAPI, Supabase & Fly.io</p>
                <p style="margin-top: 10px;">Live API: <a href="https://restless-hill-641.fly.dev" style="color: white;">restless-hill-641.fly.dev</a></p>
            </div>
        </div>

        <script>
            // Check system status
            async function checkStatus() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    document.getElementById('api-status').textContent = '✅ Online';
                    document.getElementById('db-status').textContent = data.database;
                } catch (error) {
                    document.getElementById('api-status').textContent = '❌ Error';
                    document.getElementById('db-status').textContent = '❌ Error';
                }
            }

            // Load live metrics
            async function loadMetrics() {
                try {
                    const response = await fetch('/api/dashboard/metrics');
                    const data = await response.json();
                    
                    document.getElementById('appointments').textContent = data.today_appointments || 0;
                    document.getElementById('revenue').textContent = '$' + (data.today_revenue || 0).toFixed(2);
                    document.getElementById('staff').textContent = data.active_staff || 0;
                    document.getElementById('at-risk').textContent = data.at_risk_customers || 0;
                    document.getElementById('at-risk-count').textContent = data.at_risk_customers || 0;
                } catch (error) {
                    console.error('Failed to load metrics:', error);
                }
            }

            // Run Churn Detection Agent
            async function runChurnAnalysis() {
                const container = document.getElementById('ai-insights-content');
                container.innerHTML = '<div class="loading"><div class="spinner"></div><p>AI Agent is analyzing customer data...</p></div>';
                document.getElementById('ai-status').textContent = '🔄 Analyzing...';
                
                try {
                    const response = await fetch('/api/agents/run-churn-detection', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'}
                    });
                    
                    // Log response status for debugging
                    console.log('Response status:', response.status);
                    
                    if (!response.ok) {
                        const errorText = await response.text();
                        console.error('Error response:', errorText);
                        throw new Error(`API Error (${response.status}): ${errorText}`);
                    }
                    
                    const data = await response.json();
                    console.log('Agent response:', data);
                    
                    if (data.status === 'success') {
                        displayChurnInsights(data);
                        document.getElementById('ai-status').textContent = '✅ Analysis Complete';
                    } else {
                        const errorMsg = data.detail || data.error || JSON.stringify(data);
                        container.innerHTML = '<div class="loading"><p style="color: red;">❌ Error: ' + errorMsg + '</p></div>';
                        document.getElementById('ai-status').textContent = '❌ Error';
                    }
                } catch (error) {
                    console.error('Failed to run analysis:', error);
                    container.innerHTML = '<div class="loading"><p style="color: red;">❌ Failed to run analysis: ' + error.message + '</p></div>';
                    document.getElementById('ai-status').textContent = '❌ Error';
                }
            }

            // Display churn insights
            function displayChurnInsights(data) {
                const container = document.getElementById('ai-insights-content');
                
                let html = `
                    <div class="insight-card warning">
                        <div class="insight-header">
                            <div class="insight-title">⚠️ Churn Risk Analysis</div>
                            <div class="insight-value">$${data.total_opportunity.toLocaleString()}</div>
                        </div>
                        <div class="insight-detail">
                            <strong>Analysis Summary:</strong> ${data.summary}<br>
                            <strong>Customers Analyzed:</strong> ${data.total_analyzed}<br>
                            <strong>Confidence Level:</strong> ${(data.confidence * 100).toFixed(0)}%<br>
                            <strong>Total Potential Recovery:</strong> $${data.total_opportunity.toLocaleString()}
                        </div>
                    </div>
                `;
                
                data.insights.forEach((insight, index) => {
                    html += `
                        <div class="insight-card">
                            <div class="insight-header">
                                <div class="insight-title">${insight.customer_name}</div>
                                <div class="insight-value">${(insight.churn_probability * 100).toFixed(0)}% Risk</div>
                            </div>
                            <div class="insight-detail">
                                <strong>Lifetime Value:</strong> $${insight.total_ltv.toFixed(2)}<br>
                                <strong>Days Since Visit:</strong> ${insight.days_since_visit} days<br>
                                <strong>Recommendation:</strong> ${insight.recommendation}<br>
                                <strong>Best Contact:</strong> ${insight.best_contact_time} via ${insight.preferred_channel}<br>
                                <strong>Expected Recovery:</strong> $${insight.expected_recovery.toFixed(2)}
                            </div>
                            <button class="btn btn-success" onclick="alert('Retention campaign would be triggered here!')">
                                📧 Launch Retention Campaign
                            </button>
                        </div>
                    `;
                });
                
                container.innerHTML = html;
            }

            // Placeholder for other agents
            function runSchedulerAnalysis() {
                alert('Scheduler Agent coming next! Will analyze appointment patterns and utilization.');
            }
            
            function runInventoryAnalysis() {
                alert('Inventory Agent coming next! Will predict stockouts and generate purchase orders.');
            }

            // Load on start
            checkStatus();
            loadMetrics();
            
            // Refresh every 30 seconds
            setInterval(() => {
                checkStatus();
                loadMetrics();
            }, 30000);
        </script>
    </body>
    </html>
    """

# ================================================================
# HEALTH CHECK
# ================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint for Fly.io"""
    try:
        async with db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "healthy", "database": "✅ Connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

# ================================================================
# AI AGENT ENDPOINTS - NEWLY ACTIVATED! 🤖
# ================================================================

@app.post("/api/agents/test")
async def test_agent_endpoint():
    """Simple test endpoint to verify agent infrastructure works"""
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key:
            return {
                "status": "error",
                "message": "ANTHROPIC_API_KEY not set"
            }
        
        # Try creating client
        client = anthropic.Anthropic(api_key=api_key)
        
        # Try a simple API call
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": "Say 'Agent test successful!' and nothing else."
            }]
        )
        
        response_text = message.content[0].text
        
        return {
            "status": "success",
            "message": "Agent infrastructure is working!",
            "claude_response": response_text,
            "api_key_present": True
        }
        
    except Exception as e:
        logger.error(f"Test agent error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__
        }

@app.post("/api/agents/run-churn-detection", response_model=AgentAnalysisResponse)
async def run_churn_detection_agent(conn=Depends(get_db)):
    """
    🤖 CHURN DETECTION AGENT
    
    Analyzes customer behavior to identify churn risk and generate
    personalized retention recommendations with ROI projections.
    """
    try:
        # Check for API key
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise HTTPException(status_code=503, detail="AI agents not available - ANTHROPIC_API_KEY not set")
        
        logger.info("🤖 Starting Churn Detection Agent...")
        
        # Query at-risk customers from database
        at_risk_customers = await conn.fetch("""
            SELECT 
                id,
                name,
                email,
                phone,
                last_visit,
                (CURRENT_DATE - last_visit) as days_since_visit,
                total_visits,
                total_spent,
                loyalty_points,
                preferred_services,
                communication_preference
            FROM customers
            WHERE last_visit < CURRENT_DATE - INTERVAL '45 days'
              AND last_visit >= CURRENT_DATE - INTERVAL '120 days'
              AND total_visits > 2
            ORDER BY total_spent DESC
            LIMIT 10
        """)
        
        if not at_risk_customers:
            return AgentAnalysisResponse(
                agent_type="churn_detection",
                status="success",
                total_analyzed=0,
                insights=[],
                summary="No at-risk customers found. All customers are engaged!",
                total_opportunity=0.0,
                confidence=1.0,
                timestamp=datetime.now()
            )
        
        # Prepare data for Claude
        customer_data = []
        for customer in at_risk_customers:
            customer_data.append({
                "name": customer['name'],
                "days_since_visit": customer['days_since_visit'],
                "total_visits": customer['total_visits'],
                "lifetime_value": float(customer['total_spent']),
                "preferred_services": customer['preferred_services'] or [],
                "communication_preference": customer['communication_preference']
            })
        
        # Call Claude API for analysis
        logger.info(f"📤 Sending {len(customer_data)} customers to Claude for analysis...")
        
        # Create Anthropic client (avoids startup proxy issues on Fly.io)
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""You are a customer retention expert for a spa/salon business. Analyze these at-risk customers and provide retention recommendations.

Customer Data:
{json.dumps(customer_data, indent=2)}

For each customer, provide:
1. Churn probability (0.0 to 1.0)
2. Specific retention recommendation (personalized offer)
3. Best contact time and method
4. Expected recovery value (estimated next appointment revenue)

Respond in JSON format with an array of customer insights:
{{
  "customers": [
    {{
      "name": "customer name",
      "churn_probability": 0.85,
      "recommendation": "Send 20% off Balayage service (their favorite). Emphasize we miss them.",
      "best_contact_time": "Tuesday 2pm",
      "preferred_channel": "email",
      "expected_recovery": 180.00
    }}
  ],
  "summary": "Brief overall summary of the churn situation"
}}"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Parse Claude's response
        response_text = message.content[0].text
        logger.info(f"📥 Received analysis from Claude")
        
        # Extract JSON from response
        try:
            # Try to find JSON in the response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_str = response_text[start:end]
            claude_analysis = json.loads(json_str)
        except:
            # Fallback if JSON parsing fails
            claude_analysis = {
                "customers": [],
                "summary": "Analysis completed but response format was unexpected"
            }
        
        # Build insights
        insights = []
        total_opportunity = 0.0
        
        for i, customer in enumerate(at_risk_customers):
            # Match Claude's analysis with our customer data
            claude_customer = None
            if i < len(claude_analysis.get("customers", [])):
                claude_customer = claude_analysis["customers"][i]
            
            if claude_customer:
                insight = {
                    "customer_id": str(customer['id']),
                    "customer_name": customer['name'],
                    "days_since_visit": customer['days_since_visit'],
                    "total_ltv": float(customer['total_spent']),
                    "churn_probability": claude_customer.get("churn_probability", 0.8),
                    "recommendation": claude_customer.get("recommendation", "Contact customer with personalized offer"),
                    "expected_recovery": claude_customer.get("expected_recovery", float(customer['total_spent']) * 0.25),
                    "best_contact_time": claude_customer.get("best_contact_time", "Weekday afternoon"),
                    "preferred_channel": claude_customer.get("preferred_channel", customer['communication_preference'] or "email")
                }
                insights.append(insight)
                total_opportunity += insight["expected_recovery"]
        
        # Store agent action in database
        await conn.execute("""
            INSERT INTO agent_actions (agent_id, action_type, reasoning, outcome, confidence)
            VALUES ($1, $2, $3, $4, $5)
        """, 
            "churn_detection_agent",
            "customer_retention_analysis",
            f"Analyzed {len(at_risk_customers)} at-risk customers",
            json.dumps({"total_opportunity": total_opportunity, "customers_analyzed": len(insights)}),
            0.85
        )
        
        logger.info(f"✅ Churn analysis complete: {len(insights)} customers, ${total_opportunity:.2f} opportunity")
        
        return AgentAnalysisResponse(
            agent_type="churn_detection",
            status="success",
            total_analyzed=len(insights),
            insights=insights,
            summary=claude_analysis.get("summary", f"Identified {len(insights)} high-value customers at risk of churning"),
            total_opportunity=total_opportunity,
            confidence=0.85,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"❌ Churn detection agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================
# DASHBOARD ENDPOINTS (Existing - unchanged)
# ================================================================

@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics(conn=Depends(get_db)):
    """Get key metrics for dashboard"""
    try:
        result = await conn.fetchval(
            "SELECT get_dashboard_metrics(CURRENT_DATE)"
        )
        return result
    except Exception as e:
        logger.error(f"Dashboard metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/daily-sales")
async def get_daily_sales(days: int = 30, conn=Depends(get_db)):
    """Get daily sales for the last N days"""
    try:
        sales = await conn.fetch(
            """
            SELECT * FROM vw_daily_sales
            WHERE sale_date >= CURRENT_DATE - $1::INTEGER
            ORDER BY sale_date DESC
            """,
            days
        )
        return [dict(row) for row in sales]
    except Exception as e:
        logger.error(f"Daily sales error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/staff-performance")
async def get_staff_performance(conn=Depends(get_db)):
    """Get staff performance metrics"""
    try:
        staff = await conn.fetch("SELECT * FROM vw_staff_performance")
        return [dict(row) for row in staff]
    except Exception as e:
        logger.error(f"Staff performance error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/service-performance")
async def get_service_performance(limit: int = 10, conn=Depends(get_db)):
    """Get top performing services"""
    try:
        services = await conn.fetch(
            """
            SELECT * FROM vw_service_performance
            ORDER BY total_revenue DESC
            LIMIT $1
            """,
            limit
        )
        return [dict(row) for row in services]
    except Exception as e:
        logger.error(f"Service performance error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/low-stock")
async def get_low_stock_products(conn=Depends(get_db)):
    """Get products that need reordering"""
    try:
        products = await conn.fetch("SELECT * FROM vw_low_stock_products")
        return [dict(row) for row in products]
    except Exception as e:
        logger.error(f"Low stock error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================
# CUSTOMER ENDPOINTS (Existing - unchanged)
# ================================================================

@app.get("/api/customers")
async def list_customers(limit: int = 50, offset: int = 0, conn=Depends(get_db)):
    """List all customers with pagination"""
    try:
        customers = await conn.fetch(
            """
            SELECT id, name, email, phone, total_visits, 
                   total_spent, loyalty_points, last_visit
            FROM customers
            ORDER BY total_spent DESC
            LIMIT $1 OFFSET $2
            """,
            limit, offset
        )
        return [dict(row) for row in customers]
    except Exception as e:
        logger.error(f"List customers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/at-risk")
async def get_at_risk_customers(conn=Depends(get_db)):
    """Get customers at risk of churning"""
    try:
        customers = await conn.fetch(
            """
            SELECT 
                id, name, email, phone,
                last_visit,
                (CURRENT_DATE - last_visit) as days_since_visit,
                total_visits,
                total_spent,
                loyalty_points
            FROM customers
            WHERE last_visit < CURRENT_DATE - INTERVAL '45 days'
              AND last_visit >= CURRENT_DATE - INTERVAL '120 days'
              AND total_visits > 2
            ORDER BY total_spent DESC
            LIMIT 20
            """
        )
        return [dict(row) for row in customers]
    except Exception as e:
        logger.error(f"At-risk customers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================
# SERVICES ENDPOINTS (Existing - unchanged)
# ================================================================

@app.get("/api/services")
async def list_services(category: Optional[str] = None, conn=Depends(get_db)):
    """List all available services"""
    try:
        if category:
            services = await conn.fetch(
                """
                SELECT 
                    s.id, s.name, sc.name as category,
                    s.duration_minutes, s.base_price, s.member_price,
                    s.description
                FROM services s
                JOIN service_categories sc ON s.category_id = sc.id
                WHERE s.is_active = true AND sc.name = $1
                ORDER BY s.display_order
                """,
                category
            )
        else:
            services = await conn.fetch(
                """
                SELECT 
                    s.id, s.name, sc.name as category,
                    s.duration_minutes, s.base_price, s.member_price,
                    s.description
                FROM services s
                JOIN service_categories sc ON s.category_id = sc.id
                WHERE s.is_active = true
                ORDER BY sc.display_order, s.display_order
                """
            )
        return [dict(row) for row in services]
    except Exception as e:
        logger.error(f"List services error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================
# STAFF ENDPOINTS (Existing - unchanged)
# ================================================================

@app.get("/api/staff")
async def list_staff(conn=Depends(get_db)):
    """List all active staff members"""
    try:
        staff = await conn.fetch(
            """
            SELECT 
                id, employee_number,
                first_name, last_name, email, phone,
                role, hire_date, color_code
            FROM staff
            WHERE is_active = true
            ORDER BY last_name, first_name
            """
        )
        return [dict(row) for row in staff]
    except Exception as e:
        logger.error(f"List staff error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )