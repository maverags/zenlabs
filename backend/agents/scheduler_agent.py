"""
Smart Scheduler Agent - Cloud version
"""
from backend.agents.base_agent import BaseAgent
from datetime import datetime, timedelta
import json


class SmartSchedulerAgent(BaseAgent):
    """Analyzes scheduling and identifies revenue opportunities"""
    
    def __init__(self, db_conn):
        super().__init__(
            agent_id="scheduler-001",
            role="Smart Scheduler Agent",
            db_conn=db_conn
        )
    
    def get_system_prompt(self) -> str:
        return """You are the Smart Scheduler Agent for a spa/salon.

Analyze appointment data and identify revenue optimization opportunities.

Provide:
- Utilization metrics with percentages
- Specific time slots needing attention
- Concrete recommendations with dollar amounts
- Revenue projections

Be specific and actionable. Focus on measurable business impact."""
    
    async def execute_task(self, task: Dict) -> Dict:
        task_type = task.get("type")
        
        if task_type == "analyze_utilization":
            return await self.analyze_utilization()
        elif task_type == "find_gaps":
            return await self.find_scheduling_gaps()
        else:
            return {"error": f"Unknown task: {task_type}"}
    
    async def analyze_utilization(self) -> Dict:
        """Analyze appointment utilization"""
        print(f"[{self.agent_id}] 📊 Analyzing utilization...")
        
        # Get appointment data
        appointments = await self.db.fetch(
            """SELECT 
                   DATE(scheduled_date) as date,
                   COUNT(*) as count,
                   SUM(total_amount) as revenue
               FROM appointments
               WHERE scheduled_date >= CURRENT_DATE - INTERVAL '30 days'
                 AND scheduled_date <= CURRENT_DATE
                 AND status IN ('completed', 'scheduled')
               GROUP BY DATE(scheduled_date)
               ORDER BY date DESC"""
        )
        
        if not appointments:
            return {
                "analysis": "Insufficient data",
                "metrics": {"utilization": 0, "revenue": 0}
            }
        
        data = [dict(row) for row in appointments]
        total_revenue = sum(row["revenue"] or 0 for row in data)
        avg_daily_bookings = sum(row["count"] for row in data) / len(data)
        
        # Assume 5 staff, 8 hours/day, capacity for 10 appointments/staff/day = 50/day
        capacity_per_day = 50
        avg_utilization = (avg_daily_bookings / capacity_per_day) * 100
        
        # Calculate opportunity
        if avg_utilization < 85:
            gap = (85 - avg_utilization) / 100
            avg_revenue_per_booking = total_revenue / sum(row["count"] for row in data)
            daily_opportunity = gap * capacity_per_day * avg_revenue_per_booking
            monthly_opportunity = daily_opportunity * 20
        else:
            monthly_opportunity = 0
        
        context = {
            "appointments_30d": len(data),
            "total_revenue": round(float(total_revenue), 2),
            "avg_daily_bookings": round(avg_daily_bookings, 1),
            "utilization_pct": round(avg_utilization, 1),
            "monthly_opportunity": round(monthly_opportunity, 2)
        }
        
        # Ask AI to analyze
        analysis = await self.think(
            "Analyze this 30-day utilization data. Identify patterns and provide specific recommendations to improve utilization and revenue.",
            context
        )
        
        await self.log_action(
            "utilization_analysis",
            analysis["reasoning"][:200],
            context,
            confidence=0.9
        )
        
        return {
            "analysis": analysis["reasoning"],
            "metrics": context,
            "agent": self.agent_id
        }
    
    async def find_scheduling_gaps(self) -> Dict:
        """Find low-utilization time slots"""
        print(f"[{self.agent_id}] 🔍 Finding gaps...")
        
        gaps = await self.db.fetch(
            """SELECT 
                   EXTRACT(DOW FROM scheduled_date) as day_of_week,
                   EXTRACT(HOUR FROM start_time) as hour,
                   COUNT(*) as bookings
               FROM appointments
               WHERE scheduled_date >= CURRENT_DATE - INTERVAL '60 days'
               GROUP BY day_of_week, hour
               HAVING COUNT(*) < 3
               ORDER BY bookings ASC
               LIMIT 10"""
        )
        
        if not gaps:
            return {"analysis": "No significant gaps found", "gaps": []}
        
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        gap_data = []
        
        for row in gaps:
            gap_data.append({
                "day": days[int(row["day_of_week"])],
                "hour": int(row["hour"]),
                "bookings": row["bookings"]
            })
        
        context = {
            "gaps": gap_data,
            "total_gaps": len(gap_data)
        }
        
        analysis = await self.think(
            "These time slots have low booking rates. Recommend specific strategies to fill these gaps.",
            context
        )
        
        return {
            "analysis": analysis["reasoning"],
            "gaps": gap_data[:5],
            "agent": self.agent_id
        }
