"""
FastAPI Backend for Spa/Salon AI Agent System
Complete version with dashboard UI and all API routes
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import asyncpg
import os
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel
import logging

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
    
    yield
    
    # Shutdown: Close database pool
    if db_pool:
        await db_pool.close()
        logger.info("✅ Database pool closed")

# Initialize FastAPI app
app = FastAPI(
    title="Spa Agent AI API",
    description="AI-powered spa/salon management system",
    version="1.0.0",
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

# ================================================================
# DASHBOARD UI - ROOT ENDPOINT
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
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏨 Spa Agent AI System</h1>
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
                    <span class="status-label">Environment:</span>
                    <span class="status-value">Fly.io + Supabase</span>
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
                    <div class="value" id="service-count">30</div>
                </div>

                <div class="card" onclick="window.open('/api/staff', '_blank')">
                    <h3>👥 Staff Members</h3>
                    <p>View staff roster, schedules, and availability.</p>
                    <div class="value" id="staff-count">7</div>
                </div>

                <div class="card" onclick="window.open('/api/customers/at-risk', '_blank')">
                    <h3>⚠️ At-Risk Customers</h3>
                    <p>Customers who need retention campaigns.</p>
                    <div class="value" id="at-risk-count">-</div>
                </div>

                <div class="card" onclick="window.open('/api/dashboard/low-stock', '_blank')">
                    <h3>📦 Low Stock Items</h3>
                    <p>Products that need to be reordered.</p>
                    <div class="value" id="low-stock-count">-</div>
                </div>

                <div class="card" onclick="window.open('/api/dashboard/staff-performance', '_blank')">
                    <h3>📈 Staff Performance</h3>
                    <p>View detailed staff KPIs and metrics.</p>
                    <a class="btn">View Reports</a>
                </div>

                <div class="card" onclick="window.open('/docs', '_blank')">
                    <h3>📚 API Documentation</h3>
                    <p>Interactive API docs with testing capabilities.</p>
                    <a class="btn">Open Docs</a>
                </div>
            </div>

            <div class="footer">
                <p>🚀 Powered by Claude AI, FastAPI, Supabase & Fly.io</p>
                <p style="margin-top: 10px;">Cloud-Native • Production-Ready • Live API: <a href="https://restless-hill-641.fly.dev" style="color: white;">restless-hill-641.fly.dev</a></p>
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
                    document.getElementById('low-stock-count').textContent = data.low_stock_items || 0;
                } catch (error) {
                    console.error('Failed to load metrics:', error);
                }
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
# DASHBOARD ENDPOINTS
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
# CUSTOMER ENDPOINTS
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
                EXTRACT(DAY FROM (CURRENT_DATE - last_visit))::INTEGER as days_since_visit,
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
# APPOINTMENT ENDPOINTS
# ================================================================

@app.get("/api/appointments/today")
async def get_todays_appointments(conn=Depends(get_db)):
    """Get all appointments for today"""
    try:
        appointments = await conn.fetch(
            """
            SELECT 
                a.id, a.appointment_number,
                c.name as customer_name,
                s.first_name || ' ' || s.last_name as staff_name,
                a.scheduled_date, a.start_time, a.end_time,
                a.status, a.total_amount
            FROM appointments a
            JOIN customers c ON a.customer_id = c.id
            JOIN staff s ON a.staff_id = s.id
            WHERE a.scheduled_date = CURRENT_DATE
            ORDER BY a.start_time
            """
        )
        return [dict(row) for row in appointments]
    except Exception as e:
        logger.error(f"Today's appointments error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/appointments/upcoming")
async def get_upcoming_appointments(days: int = 7, conn=Depends(get_db)):
    """Get upcoming appointments for the next N days"""
    try:
        appointments = await conn.fetch(
            """
            SELECT 
                a.id, a.appointment_number,
                c.name as customer_name,
                s.first_name || ' ' || s.last_name as staff_name,
                a.scheduled_date, a.start_time,
                a.status, a.total_amount
            FROM appointments a
            JOIN customers c ON a.customer_id = c.id
            JOIN staff s ON a.staff_id = s.id
            WHERE a.scheduled_date BETWEEN CURRENT_DATE AND CURRENT_DATE + $1::INTEGER
              AND a.status NOT IN ('cancelled', 'no-show')
            ORDER BY a.scheduled_date, a.start_time
            """,
            days
        )
        return [dict(row) for row in appointments]
    except Exception as e:
        logger.error(f"Upcoming appointments error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================
# SERVICES ENDPOINTS
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

@app.get("/api/services/categories")
async def list_service_categories(conn=Depends(get_db)):
    """List all service categories"""
    try:
        categories = await conn.fetch(
            """
            SELECT id, name, description
            FROM service_categories
            WHERE active = true
            ORDER BY display_order
            """
        )
        return [dict(row) for row in categories]
    except Exception as e:
        logger.error(f"Service categories error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================
# STAFF ENDPOINTS
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

@app.get("/api/staff/{staff_id}/availability")
async def get_staff_availability(staff_id: str, conn=Depends(get_db)):
    """Get availability schedule for a staff member"""
    try:
        availability = await conn.fetch(
            """
            SELECT 
                day_of_week, start_time, end_time,
                break_start, break_end
            FROM staff_availability
            WHERE staff_id = $1::UUID AND is_available = true
            ORDER BY day_of_week
            """,
            staff_id
        )
        return [dict(row) for row in availability]
    except Exception as e:
        logger.error(f"Staff availability error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================
# INVENTORY ENDPOINTS
# ================================================================

@app.get("/api/inventory/products")
async def list_products(category: Optional[str] = None, conn=Depends(get_db)):
    """List retail products"""
    try:
        if category:
            products = await conn.fetch(
                """
                SELECT id, sku, name, category, brand,
                       retail_price, current_stock, reorder_point
                FROM retail_products
                WHERE is_active = true AND category = $1
                ORDER BY name
                """,
                category
            )
        else:
            products = await conn.fetch(
                """
                SELECT id, sku, name, category, brand,
                       retail_price, current_stock, reorder_point
                FROM retail_products
                WHERE is_active = true
                ORDER BY category, name
                """
            )
        return [dict(row) for row in products]
    except Exception as e:
        logger.error(f"List products error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================================================
# ERROR HANDLERS
# ================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG") else "An error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )