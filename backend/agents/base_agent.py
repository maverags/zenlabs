"""
Base Agent - Cloud-native version for Supabase
"""
from typing import Dict, List, Any, Optional
from anthropic import Anthropic
import json
from datetime import datetime
import os


class BaseAgent:
    """Base class for all AI agents - optimized for cloud deployment"""
    
    def __init__(self, agent_id: str, role: str, db_conn):
        self.agent_id = agent_id
        self.role = role
        self.db = db_conn
        
        # Initialize Anthropic client
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        
        print(f"[{self.agent_id}] ✓ Initialized")
    
    async def think(self, task: str, context: Dict = None) -> Dict:
        """Core reasoning - agent thinks using Claude"""
        system_prompt = self.get_system_prompt()
        
        context_str = ""
        if context:
            context_str = f"\n\nContext:\n{json.dumps(context, indent=2, default=str)}"
        
        user_message = f"{task}{context_str}"
        
        print(f"[{self.agent_id}] 🤔 Thinking...")
        
        start = datetime.now()
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        
        elapsed = (datetime.now() - start).total_seconds() * 1000
        
        reasoning = response.content[0].text
        
        result = {
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_id,
            "execution_time_ms": int(elapsed)
        }
        
        # Store in memory
        await self.log_action(
            "thinking",
            f"Task: {task[:100]}",
            result,
            confidence=0.9
        )
        
        return result
    
    async def log_action(
        self,
        action_type: str,
        reasoning: str,
        outcome: Dict,
        confidence: Optional[float] = None
    ):
        """Log action for audit trail"""
        try:
            await self.db.execute(
                """INSERT INTO agent_actions 
                   (agent_id, action_type, reasoning, outcome, confidence)
                   VALUES ($1, $2, $3, $4, $5)""",
                self.agent_id,
                action_type,
                reasoning,
                json.dumps(outcome, default=str),
                confidence
            )
        except Exception as e:
            print(f"[{self.agent_id}] ⚠ Could not log: {e}")
    
    def get_system_prompt(self) -> str:
        """Override in subclasses"""
        return f"You are {self.role}. Analyze data and provide actionable insights."
    
    async def execute_task(self, task: Dict) -> Dict:
        """Override in subclasses"""
        raise NotImplementedError(f"{self.agent_id} must implement execute_task")
