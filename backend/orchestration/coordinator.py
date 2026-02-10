"""
Agent Coordinator - Cloud version
"""
from datetime import datetime


class AgentCoordinator:
    """Orchestrates multi-agent workflows"""
    
    def __init__(self, db_conn):
        self.agents = {}
        self.db = db_conn
        print("[Coordinator] ✓ Initialized")
    
    def register_agent(self, agent):
        """Register an agent"""
        self.agents[agent.agent_id] = agent
        print(f"[Coordinator] ✓ Registered {agent.agent_id}")
    
    async def run_workflow(self, workflow_name: str) -> dict:
        """Execute coordinated workflow"""
        print(f"\n{'='*60}")
        print(f"[Coordinator] 🚀 Starting workflow: {workflow_name}")
        print(f"{'='*60}\n")
        
        if workflow_name == "daily_analysis":
            return await self.daily_analysis_workflow()
        elif workflow_name == "churn_prevention":
            return await self.churn_prevention_workflow()
        else:
            return {"error": f"Unknown workflow: {workflow_name}"}
    
    async def daily_analysis_workflow(self) -> dict:
        """Daily business analysis"""
        print("[Workflow] 🌅 Daily Analysis Starting...")
        
        results = {
            "workflow": "daily_analysis",
            "timestamp": datetime.now().isoformat()
        }
        
        scheduler = self.agents.get("scheduler-001")
        client_agent = self.agents.get("client-intel-001")
        
        if not scheduler or not client_agent:
            return {"error": "Required agents not found"}
        
        # Run analyses
        print("\n[Step 1] Scheduler analyzing utilization...")
        results["utilization"] = await scheduler.execute_task({
            "type": "analyze_utilization"
        })
        
        print("\n[Step 2] Client Intelligence detecting churn...")
        results["churn_risk"] = await client_agent.execute_task({
            "type": "detect_churn_risk"
        })
        
        print("\n[Workflow] ✅ Daily Analysis Complete!\n")
        
        return results
    
    async def churn_prevention_workflow(self) -> dict:
        """Coordinated churn prevention"""
        print("[Workflow] 🎯 Churn Prevention Starting...")
        
        results = {
            "workflow": "churn_prevention",
            "timestamp": datetime.now().isoformat()
        }
        
        client_agent = self.agents.get("client-intel-001")
        
        if not client_agent:
            return {"error": "Client Intelligence agent not found"}
        
        # Detect at-risk customers
        print("\n[Step 1] Identifying at-risk customers...")
        churn_data = await client_agent.execute_task({
            "type": "detect_churn_risk"
        })
        
        results["at_risk_summary"] = churn_data.get("summary", {})
        results["recommendations"] = churn_data.get("at_risk_customers", [])
        
        print("\n[Workflow] ✅ Churn Prevention Complete!\n")
        
        return results
