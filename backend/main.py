"""
Main FastAPI Application - Spa/Salon Agentic System
Cloud-native deployment for Fly.io
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
from datetime import datetime, date
import asyncpg
from contextlib import asynccontextmanager

# Import agents (we'll create these next)
from backend.agents.scheduler_agent import SmartSchedulerAgent
from backend.agents.client_intelligence_agent import ClientIntelligenceAgent
from backend.orchestration.coordinator import AgentCoordinator

# Global database connection pool
db_pool = None
coordinator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global db_pool, coordinator
    
    # Startup: Create database pool
    print("🚀 Starting application...")
    db_pool = await asyncpg.create_pool(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT', 5432)),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        ssl='require',
        min_size=2,
        max_size=10
    )
    
    # Initialize agents
    async with db_pool.acquire() as conn:
        scheduler = SmartSchedulerAgent(conn)
        client_intel = ClientIntelligenceAgent(conn)
        
        coordinator = AgentCoordinator(conn)
        coordinator.register_agent(scheduler)
        coordinator.register_agent(client_intel)
    
    print("✅ Application ready!")
    
    yield
    
    # Shutdown: Close database pool
    await db_pool.close()
    print("👋 Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Spa/Salon Agentic System",
    description="AI-powered spa/salon management with autonomous agents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================================================
# PYDANTIC MODELS
# ================================================================

class CustomerCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: str
    notes: Optional[str] = None

class AppointmentCreate(BaseModel):
    customer_id: str
    staff_id: str
    service_ids: List[str]
    scheduled_date: date
    start_time: str
    notes: Optional[str] = None

class SaleCreate(BaseModel):
    customer_id: Optional[str] = None
    staff_id: str
    items: List[Dict[str, Any]]
    payment_method: str
    tip_amount: float = 0

# ================================================================
# HEALTH CHECK
# ================================================================

@app.get("/")
async def root():
    """Health check and API info"""
    return {
        "status": "healthy",
        "service": "Spa/Salon Agentic System",
        "version": "1.0.0",
        "endpoints": {
            "dashboard": "/dashboard",
            "customers": "/api/customers",
            "appointments": "/api/appointments",
            "staff": "/api/staff",
            "services": "/api/services",
            "sales": "/api/sales",
            "agents": "/api/agents",
            "reports": "/api/reports"
        }
    }

# ================================================================
# DASHBOARD (HTML)
# ================================================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard UI"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Spa/Salon AI Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container { max-width: 1400px; margin: 0 auto; }
            .header {
                background: white;
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 { color: #667eea; font-size: 2.5em; margin-bottom: 10px; }
            .subtitle { color: #666; font-size: 1.1em; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .card {
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                transition: transform 0.3s ease;
            }
            .card:hover { transform: translateY(-5px); }
            .card h3 { color: #667eea; margin-bottom: 15px; font-size: 1.3em; }
            .metric {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 0;
                border-bottom: 1px solid #eee;
            }
            .metric:last-child { border-bottom: none; }
            .metric-value { 
                font-size: 1.8em; 
                font-weight: bold; 
                color: #764ba2; 
            }
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 8px;
                font-size: 1em;
                cursor: pointer;
                margin: 5px;
                transition: all 0.3s;
            }
            .btn:hover { 
                transform: scale(1.05);
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
            }
            .agent-status {
                background: #f0f4ff;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
            }
            .loading {
                text-align: center;
                padding: 40px;
                color: #667eea;
                font-size: 1.2em;
            }
            .actions { text-align: center; padding: 20px; }
            pre {
                background: #f5f5f5;
                padding: 15px;
                border-radius: 8px;
                overflow-x: auto;
                max-height: 400px;
                overflow-y: auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏨 Spa/Salon AI Management System</h1>
                <p class="subtitle">Autonomous AI agents running your business operations</p>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h3>📊 Today's Overview</h3>
                    <div id="overview">
                        <div class="loading">Loading data...</div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>👥 Staff Status</h3>
                    <div id="staff">
                        <div class="loading">Loading staff...</div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🤖 AI Agent Activity</h3>
                    <div id="agents">
                        <div class="loading">Loading agents...</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>🎯 AI Agent Analysis</h3>
                <div class="actions">
                    <button class="btn" onclick="runAnalysis('utilization')">
                        📈 Analyze Utilization
                    </button>
                    <button class="btn" onclick="runAnalysis('churn')">
                        ⚠️ Detect Churn Risk
                    </button>
                    <button class="btn" onclick="runAnalysis('daily')">
                        🌅 Daily Business Analysis
                    </button>
                </div>
                <div id="analysis-results"></div>
            </div>
            
            <div class="card">
                <h3>📈 Revenue Reports</h3>
                <div id="reports">
                    <div class="loading">Loading reports...</div>
                </div>
            </div>
        </div>
        
        <script>
            // Load initial data
            async function loadData() {
                try {
                    // Load overview
                    const overview = await fetch('/api/reports/overview').then(r => r.json());
                    document.getElementById('overview').innerHTML = `
                        <div class="metric">
                            <span>Today's Appointments</span>
                            <span class="metric-value">${overview.appointments_today || 0}</span>
                        </div>
                        <div class="metric">
                            <span>Active Customers</span>
                            <span class="metric-value">${overview.total_customers || 0}</span>
                        </div>
                        <div class="metric">
                            <span>Revenue (30d)</span>
                            <span class="metric-value">$${(overview.revenue_30d || 0).toLocaleString()}</span>
                        </div>
                    `;
                    
                    // Load staff
                    const staff = await fetch('/api/staff').then(r => r.json());
                    document.getElementById('staff').innerHTML = staff.map(s => `
                        <div class="agent-status">
                            <strong>${s.first_name} ${s.last_name}</strong> - ${s.role}
                            <br><small>Commission: ${s.commission_rate}%</small>
                        </div>
                    `).join('');
                    
                    // Load agent activity
                    const agents = await fetch('/api/agents/activity').then(r => r.json());
                    document.getElementById('agents').innerHTML = agents.slice(0, 5).map(a => `
                        <div class="agent-status">
                            <strong>${a.agent_id}</strong>: ${a.action_type}
                            <br><small>${new Date(a.created_at).toLocaleString()}</small>
                        </div>
                    `).join('') || '<p>No agent activity yet</p>';
                    
                    // Load reports
                    const reports = await fetch('/api/reports/daily-sales').then(r => r.json());
                    document.getElementById('reports').innerHTML = `
                        <pre>${JSON.stringify(reports.slice(0, 7), null, 2)}</pre>
                    `;
                    
                } catch (error) {
                    console.error('Error loading data:', error);
                }
            }
            
            // Run AI analysis
            async function runAnalysis(type) {
                const resultsDiv = document.getElementById('analysis-results');
                resultsDiv.innerHTML = '<div class="loading">🤖 AI agents analyzing data...</div>';
                
                try {
                    const response = await fetch(`/api/agents/analyze/${type}`);
                    const result = await response.json();
                    
                    resultsDiv.innerHTML = `
                        <div class="agent-status">
                            <h4>Analysis Complete!</h4>
                            <pre>${JSON.stringify(result, null, 2)}</pre>
                        </div>
                    `;
                } catch (error) {
                    resultsDiv.innerHTML = `<div class="agent-status" style="border-color: red;">
                        Error: ${error.message}
                    </div>`;
                }
            }
            
            // Load data on page load
            loadData();
            
            // Refresh every 30 seconds
            setInterval(loadData, 30000);
        </script>
    </body>
    </html>
    """
    return html

# ================================================================
# API ENDPOINTS - CUSTOMERS
# ================================================================

@app.get("/api/customers")
async def get_customers(limit: int = 50):
    """Get all customers"""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM customers ORDER BY created_at DESC LIMIT $1",
            limit
        )
        return [dict(row) for row in rows]

@app.post("/api/customers")
async def create_customer(customer: CustomerCreate):
    """Create new customer"""
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO customers (name, email, phone, notes)
               VALUES ($1, $2, $3, $4)
               RETURNING *""",
            customer.name, customer.email, customer.phone, customer.notes
        )
        return dict(row)

# ================================================================
# API ENDPOINTS - APPOINTMENTS
# ================================================================

@app.get("/api/appointments")
async def get_appointments(date: Optional[str] = None):
    """Get appointments, optionally filtered by date"""
    async with db_pool.acquire() as conn:
        if date:
            rows = await conn.fetch(
                """SELECT a.*, c.name as customer_name, 
                          s.first_name || ' ' || s.last_name as staff_name
                   FROM appointments a
                   LEFT JOIN customers c ON a.customer_id = c.id
                   LEFT JOIN staff s ON a.staff_id = s.id
                   WHERE a.scheduled_date = $1
                   ORDER BY a.start_time""",
                date
            )
        else:
            rows = await conn.fetch(
                """SELECT a.*, c.name as customer_name,
                          s.first_name || ' ' || s.last_name as staff_name
                   FROM appointments a
                   LEFT JOIN customers c ON a.customer_id = c.id
                   LEFT JOIN staff s ON a.staff_id = s.id
                   ORDER BY a.scheduled_date DESC, a.start_time
                   LIMIT 100"""
            )
        return [dict(row) for row in rows]

@app.get("/api/appointments/today")
async def get_todays_appointments():
    """Get today's appointments"""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT a.*, c.name as customer_name,
                      s.first_name || ' ' || s.last_name as staff_name
               FROM appointments a
               LEFT JOIN customers c ON a.customer_id = c.id
               LEFT JOIN staff s ON a.staff_id = s.id
               WHERE a.scheduled_date = CURRENT_DATE
               ORDER BY a.start_time"""
        )
        return [dict(row) for row in rows]

# ================================================================
# API ENDPOINTS - STAFF
# ================================================================

@app.get("/api/staff")
async def get_staff():
    """Get all staff members"""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM staff WHERE is_active = true ORDER BY first_name"
        )
        return [dict(row) for row in rows]

@app.get("/api/staff/{staff_id}/schedule")
async def get_staff_schedule(staff_id: str):
    """Get staff member's schedule"""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM staff_availability WHERE staff_id = $1 ORDER BY day_of_week",
            staff_id
        )
        return [dict(row) for row in rows]

# ================================================================
# API ENDPOINTS - SERVICES
# ================================================================

@app.get("/api/services")
async def get_services():
    """Get all active services"""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT s.*, sc.name as category_name
               FROM services s
               JOIN service_categories sc ON s.category_id = sc.id
               WHERE s.is_active = true
               ORDER BY sc.display_order, s.display_order"""
        )
        return [dict(row) for row in rows]

@app.get("/api/services/categories")
async def get_service_categories():
    """Get all service categories"""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM service_categories WHERE active = true ORDER BY display_order"
        )
        return [dict(row) for row in rows]

# ================================================================
# API ENDPOINTS - REPORTS
# ================================================================

@app.get("/api/reports/overview")
async def get_overview():
    """Get business overview metrics"""
    async with db_pool.acquire() as conn:
        result = await conn.fetchrow(
            """SELECT 
                (SELECT COUNT(*) FROM customers) as total_customers,
                (SELECT COUNT(*) FROM appointments 
                 WHERE scheduled_date = CURRENT_DATE) as appointments_today,
                (SELECT COALESCE(SUM(total_amount), 0) FROM sales 
                 WHERE sale_date >= CURRENT_DATE - INTERVAL '30 days') as revenue_30d,
                (SELECT COUNT(*) FROM staff WHERE is_active = true) as active_staff
            """
        )
        return dict(result)

@app.get("/api/reports/daily-sales")
async def get_daily_sales(days: int = 30):
    """Get daily sales summary"""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM vw_daily_sales LIMIT $1",
            days
        )
        return [dict(row) for row in rows]

@app.get("/api/reports/staff-performance")
async def get_staff_performance():
    """Get staff performance metrics"""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM vw_staff_performance")
        return [dict(row) for row in rows]

@app.get("/api/reports/low-stock")
async def get_low_stock():
    """Get low stock products"""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM vw_low_stock")
        return [dict(row) for row in rows]

# ================================================================
# API ENDPOINTS - AI AGENTS
# ================================================================

@app.get("/api/agents/activity")
async def get_agent_activity(limit: int = 20):
    """Get recent agent actions"""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT * FROM agent_actions 
               ORDER BY created_at DESC 
               LIMIT $1""",
            limit
        )
        return [dict(row) for row in rows]

@app.get("/api/agents/analyze/{analysis_type}")
async def run_agent_analysis(analysis_type: str):
    """Run AI agent analysis"""
    global coordinator
    
    async with db_pool.acquire() as conn:
        # Recreate coordinator with fresh connection
        scheduler = SmartSchedulerAgent(conn)
        client_intel = ClientIntelligenceAgent(conn)
        
        temp_coordinator = AgentCoordinator(conn)
        temp_coordinator.register_agent(scheduler)
        temp_coordinator.register_agent(client_intel)
        
        if analysis_type == "utilization":
            result = await scheduler.execute_task({"type": "analyze_utilization"})
        elif analysis_type == "churn":
            result = await client_intel.execute_task({"type": "detect_churn_risk"})
        elif analysis_type == "daily":
            result = await temp_coordinator.run_workflow("daily_analysis")
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")
        
        return result

@app.post("/api/agents/workflow/{workflow_name}")
async def run_workflow(workflow_name: str):
    """Execute multi-agent workflow"""
    async with db_pool.acquire() as conn:
        scheduler = SmartSchedulerAgent(conn)
        client_intel = ClientIntelligenceAgent(conn)
        
        temp_coordinator = AgentCoordinator(conn)
        temp_coordinator.register_agent(scheduler)
        temp_coordinator.register_agent(client_intel)
        
        result = await temp_coordinator.run_workflow(workflow_name)
        return result

# ================================================================
# ERROR HANDLERS
# ================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "path": str(request.url)}

@app.exception_handler(500)
async def server_error_handler(request, exc):
    return {"error": "Internal server error", "detail": str(exc)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
