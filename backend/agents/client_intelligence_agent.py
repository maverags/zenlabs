"""
Client Intelligence Agent - Cloud version
"""
from backend.agents.base_agent import BaseAgent
from datetime import datetime, timedelta


class ClientIntelligenceAgent(BaseAgent):
    """Detects churn risk and manages customer retention"""
    
    def __init__(self, db_conn):
        super().__init__(
            agent_id="client-intel-001",
            role="Client Intelligence Agent",
            db_conn=db_conn
        )
    
    def get_system_prompt(self) -> str:
        return """You are the Client Intelligence Agent for a spa/salon.

Your role: Maximize customer retention and lifetime value.

For at-risk customers, provide:
- Risk assessment (High/Medium/Low) with reasoning
- Specific churn indicators
- Personalized retention strategies
- Recommended offers with percentages
- Communication approach

Be empathetic and specific. Focus on high-value customers first."""
    
    async def execute_task(self, task: Dict) -> Dict:
        task_type = task.get("type")
        
        if task_type == "detect_churn_risk":
            return await self.detect_churn_risk()
        elif task_type == "segment_customers":
            return await self.segment_customers()
        else:
            return {"error": f"Unknown task: {task_type}"}
    
    async def detect_churn_risk(self) -> Dict:
        """Identify at-risk customers"""
        print(f"[{self.agent_id}] ⚠️  Detecting churn risk...")
        
        # Find customers who haven't visited recently
        at_risk = await self.db.fetch(
            """SELECT 
                   c.*,
                   EXTRACT(DAY FROM (CURRENT_DATE - c.last_visit)) as days_since_visit
               FROM customers c
               WHERE c.last_visit < CURRENT_DATE - INTERVAL '45 days'
                 AND c.last_visit >= CURRENT_DATE - INTERVAL '120 days'
                 AND c.total_visits >= 3
               ORDER BY c.total_spent DESC
               LIMIT 10"""
        )
        
        if not at_risk:
            return {
                "at_risk_customers": [],
                "analysis": "No at-risk customers detected",
                "summary": {"total_at_risk": 0, "value_at_risk": 0}
            }
        
        at_risk_data = []
        total_value = 0
        
        for row in at_risk:
            customer = {
                "id": str(row["id"]),
                "name": row["name"],
                "email": row["email"],
                "phone": row["phone"],
                "days_since_visit": int(row["days_since_visit"]),
                "total_visits": row["total_visits"],
                "total_spent": float(row["total_spent"]),
                "preferred_services": row["preferred_services"]
            }
            
            # Assign risk level
            if customer["total_spent"] > 1000 and customer["days_since_visit"] > 60:
                customer["risk_level"] = "HIGH"
            elif customer["total_spent"] > 500 or customer["days_since_visit"] > 75:
                customer["risk_level"] = "MEDIUM"
            else:
                customer["risk_level"] = "LOW"
            
            at_risk_data.append(customer)
            total_value += customer["total_spent"]
        
        summary = {
            "total_at_risk": len(at_risk_data),
            "high_risk": len([c for c in at_risk_data if c["risk_level"] == "HIGH"]),
            "value_at_risk": round(total_value, 2)
        }
        
        context = {
            "at_risk_customers": at_risk_data[:5],
            "summary": summary
        }
        
        # Get AI analysis
        analysis = await self.think(
            f"Analyze these {len(at_risk_data)} at-risk customers. For each HIGH risk customer, create a retention strategy with specific offers and messaging.",
            context
        )
        
        await self.log_action(
            "churn_detection",
            analysis["reasoning"][:200],
            summary,
            confidence=0.88
        )
        
        return {
            "at_risk_customers": at_risk_data[:5],
            "summary": summary,
            "analysis": analysis["reasoning"],
            "agent": self.agent_id
        }
    
    async def segment_customers(self) -> Dict:
        """Segment customers by value and behavior"""
        print(f"[{self.agent_id}] 📊 Segmenting customers...")
        
        segments = await self.db.fetch(
            """SELECT 
                   CASE 
                       WHEN total_spent > 1500 AND total_visits > 10 THEN 'VIP'
                       WHEN total_spent > 500 AND total_visits > 5 THEN 'Regular'
                       WHEN total_visits <= 2 THEN 'New'
                       ELSE 'Occasional'
                   END as segment,
                   COUNT(*) as customer_count,
                   AVG(total_spent) as avg_ltv,
                   AVG(total_visits) as avg_visits
               FROM customers
               GROUP BY segment"""
        )
        
        segment_data = []
        for row in segments:
            segment_data.append({
                "segment": row["segment"],
                "count": row["customer_count"],
                "avg_ltv": round(float(row["avg_ltv"]), 2),
                "avg_visits": round(float(row["avg_visits"]), 1)
            })
        
        context = {"segments": segment_data}
        
        analysis = await self.think(
            "Analyze these customer segments. Recommend specific strategies for each segment to maximize value.",
            context
        )
        
        return {
            "segments": segment_data,
            "analysis": analysis["reasoning"],
            "agent": self.agent_id
        }
