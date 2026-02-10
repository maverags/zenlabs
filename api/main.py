"""
SPA/SALON MANAGEMENT SYSTEM - FastAPI Application
Cloud-native API with AI agents for Supabase + Fly.io
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import asyncpg
import os
from datetime import datetime, date, time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, UUID4
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection pool
db_pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage database connection pool lifecycle"""
    global db_pool
    
    # Startup
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set!")
        raise ValueError("DATABASE_URL environment variable required")
    
    try:
        db_pool = await asyncpg.create_pool(
            database_url,
            min_size=2,
            max_size=10,
            command_timeout=60
        )
        logger.info("✅ Database pool created")
    except Exception as e:
        logger.error(f"❌ Failed to create database pool: {e}")
        raise
    
    yield
    
    # Shutdown
    if db_pool:
        await db_pool.close()
        logger.info("Database pool closed")

# Initialize FastAPI
app = FastAPI(
    title="Spa/Salon Management API",
    description="AI-powered spa and salon management system",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================================================
# PYDANTIC MODELS
# ================================================================

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database: str
    version: str

class DailySalesReport(BaseModel):
    sale_date: date
    transaction_count: int
    subtotal: float
    total_discounts: float
    total_tax: float
    total_tips: float
    total_revenue: float
    avg_ticket_size: float

class StaffPerformance(BaseModel):
    staff_id: UUID4
    staff_name: str
    role: str
    appointments_completed: int
    service_revenue: float
    retail_transactions: int
    retail_revenue: float
    total_commission: float

class ServicePerformance(BaseModel):
    category: str
    service_name: str
    duration_minutes: int
    base_price: float
    times_booked: int
    total_revenue: float
    avg_price: float

class AgentAnalysisRequest(BaseModel):
    agent_type: str  # 'scheduler', 'client_intelligence', 'inventory', 'all'
    date_range_days: Optional[int] = 30

class AgentAnalysisResponse(BaseModel):
    agent_id: str
    analysis: str
    metrics: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime

# ================================================================
# HELPER FUNCTIONS
# ================================================================

async def get_db_connection():
    """Get database connection from pool"""
    if not db_pool:
        raise HTTPException(status_code=503, detail="Database pool not initialized")
    return await db_pool.acquire()

async def release_db_connection(conn):
    """Release database connection back to pool"""
    if conn:
        await db_pool.release(conn)

# ================================================================
# HEALTH & STATUS ENDPOINTS
# ================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main dashboard"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Spa/Salon Management System</title>
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
                max-width: 1200px;
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
            .btn {
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 600;
                transition: background 0.3s ease;
            }
            .btn:hover {
                background: #5568d3;
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
                <h1>🏨 Spa/Salon Management System</h1>
                <p>AI-Powered Business Operations Platform</p>
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
                    <span class="status-value" id="agents-status">Loading...</span>
                </div>
            </div>

            <div class="cards">
                <div class="card">
                    <h3>📊 Analytics Dashboard</h3>
                    <p>View real-time business metrics, sales reports, and performance analytics.</p>
                    <a href="/api/docs" class="btn" target="_blank">View Reports</a>
                </div>

                <div class="card">
                    <h3>🤖 AI Agent Analysis</h3>
                    <p>Run autonomous AI agents to analyze operations and identify opportunities.</p>
                    <a href="#" class="btn" onclick="runAgents(); return false;">Run Analysis</a>
                </div>

                <div class="card">
                    <h3>📅 Appointment System</h3>
                    <p>Manage bookings, staff schedules, and customer appointments.</p>
                    <a href="/api/docs#/appointments" class="btn" target="_blank">Manage Bookings</a>
                </div>

                <div class="card">
                    <h3>💰 Point of Sale</h3>
                    <p>Process transactions, track sales, and manage inventory.</p>
                    <a href="/api/docs#/sales" class="btn" target="_blank">View POS</a>
                </div>

                <div class="card">
                    <h3>📈 Business Reports</h3>
                    <p>Daily sales, staff performance, service analytics, and projections.</p>
                    <a href="/api/reports/summary" class="btn" target="_blank">View Reports</a>
                </div>

                <div class="card">
                    <h3>🔧 API Documentation</h3>
                    <p>Interactive API docs with testing capabilities for developers.</p>
                    <a href="/api/docs" class="btn" target="_blank">API Docs</a>
                </div>
            </div>

            <div class="footer">
                <p>Powered by Claude AI, FastAPI, Supabase & Fly.io</p>
                <p style="margin-top: 10px;">Cloud-Native • Production-Ready • Auto-Scaling</p>
            </div>
        </div>

        <script>
            // Check system status
            async function checkStatus() {
                try {
                    const response = await fetch('/api/health');
                    const data = await response.json();
                    document.getElementById('api-status').textContent = '✅ Online';
                    document.getElementById('db-status').textContent = data.database;
                    document.getElementById('agents-status').textContent = '✅ Ready';
                } catch (error) {
                    document.getElementById('api-status').textContent = '❌ Error';
                    document.getElementById('db-status').textContent = '❌ Error';
                    document.getElementById('agents-status').textContent = '❌ Error';
                }
            }

            // Run AI agents
            async function runAgents() {
                if (confirm('This will run AI agent analysis on your data. Continue?')) {
                    alert('AI agents started! Check the API docs at /api/agents/status for results.');
                    window.open('/api/docs#/agents/run_agent_analysis_api_agents_analyze_post', '_blank');
                }
            }

            // Check status on load
            checkStatus();
            // Refresh every 30 seconds
            setInterval(checkStatus, 30000);
        </script>
    </body>
    </html>
    """

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    conn = await get_db_connection()
    try:
        # Test database connection
        db_version = await conn.fetchval("SELECT version()")
        db_status = "✅ Connected" if db_version else "❌ Error"
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            database=db_status,
            version="2.0.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")
    finally:
        await release_db_connection(conn)

# ================================================================
# REPORTS ENDPOINTS
# ================================================================

@app.get("/api/reports/daily-sales", response_model=List[DailySalesReport])
async def get_daily_sales(days: int = 30):
    """Get daily sales summary"""
    conn = await get_db_connection()
    try:
        rows = await conn.fetch("""
            SELECT * FROM vw_daily_sales
            WHERE sale_date >= CURRENT_DATE - $1
            ORDER BY sale_date DESC
        """, days)
        
        return [dict(row) for row in rows]
    finally:
        await release_db_connection(conn)

@app.get("/api/reports/staff-performance", response_model=List[StaffPerformance])
async def get_staff_performance():
    """Get staff performance metrics"""
    conn = await get_db_connection()
    try:
        rows = await conn.fetch("SELECT * FROM vw_staff_performance ORDER BY service_revenue DESC")
        return [dict(row) for row in rows]
    finally:
        await release_db_connection(conn)

@app.get("/api/reports/service-performance", response_model=List[ServicePerformance])
async def get_service_performance():
    """Get service performance analytics"""
    conn = await get_db_connection()
    try:
        rows = await conn.fetch("SELECT * FROM vw_service_performance ORDER BY total_revenue DESC LIMIT 20")
        return [dict(row) for row in rows]
    finally:
        await release_db_connection(conn)

@app.get("/api/reports/summary")
async def get_business_summary():
    """Get comprehensive business summary"""
    conn = await get_db_connection()
    try:
        # Get various metrics
        total_customers = await conn.fetchval("SELECT COUNT(*) FROM customers")
        total_appointments_today = await conn.fetchval(
            "SELECT COUNT(*) FROM appointments WHERE scheduled_date = CURRENT_DATE"
        )
        total_revenue_today = await conn.fetchval(
            "SELECT COALESCE(SUM(total_amount), 0) FROM sales WHERE DATE(sale_date) = CURRENT_DATE"
        )
        active_staff = await conn.fetchval("SELECT COUNT(*) FROM staff WHERE is_active = true")
        
        return {
            "snapshot": {
                "total_customers": total_customers,
                "appointments_today": total_appointments_today,
                "revenue_today": float(total_revenue_today) if total_revenue_today else 0,
                "active_staff": active_staff,
                "timestamp": datetime.now()
            }
        }
    finally:
        await release_db_connection(conn)

# ================================================================
# AI AGENTS ENDPOINT (Placeholder - full implementation coming)
# ================================================================

@app.post("/api/agents/analyze", response_model=AgentAnalysisResponse)
async def run_agent_analysis(request: AgentAnalysisRequest, background_tasks: BackgroundTasks):
    """
    Run AI agent analysis on business data
    
    This is a simplified version - full agent implementation
    will include the scheduler, client intelligence, and inventory agents
    """
    conn = await get_db_connection()
    try:
        # Get some basic metrics for demo
        utilization = await conn.fetchval("""
            SELECT COUNT(*) * 100.0 / (
                SELECT COUNT(*) FROM staff_availability WHERE is_available = true
            )
            FROM appointments 
            WHERE scheduled_date >= CURRENT_DATE - 30
        """)
        
        return AgentAnalysisResponse(
            agent_id="demo-agent",
            analysis=f"Analyzed {request.date_range_days} days of data. System utilization at {utilization:.1f}%",
            metrics={
                "utilization_rate": float(utilization) if utilization else 0,
                "date_range": request.date_range_days
            },
            recommendations=[
                "Schedule optimization recommended",
                "Customer retention campaigns suggested",
                "Inventory reorder points need review"
            ],
            timestamp=datetime.now()
        )
    finally:
        await release_db_connection(conn)

# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
