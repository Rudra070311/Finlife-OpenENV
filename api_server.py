"""
FinLife-OpenEnv API Server
REST API for OpenEnv spec compliance with step()/reset()/state() endpoints
"""

import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import json
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from app.config import EnvConfig
from app.environment_enhanced import EnhancedFinLifeEnv
from app.models.action import Action
from app.logic.graders.finlife_graders import grade_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global environment instance
env = None
current_task = "wealth_accumulation"
episode_data = {}
env_config = EnvConfig()  # Create instance of EnvConfig

app = FastAPI(title="FinLife-OpenEnv", version="2.0")


class ResetRequest(BaseModel):
    task: str = "wealth_accumulation"


class StepRequest(BaseModel):
    action: Dict[str, Any]


class StatusResponse(BaseModel):
    status: str
    task: str
    step: int
    done: bool


@app.get("/status")
async def status() -> StatusResponse:
    """Health check endpoint"""
    global env
    if env is None:
        raise HTTPException(status_code=503, detail="Environment not initialized")
    
    return StatusResponse(
        status="healthy",
        task=current_task,
        step=env.step_count,
        done=False
    )


@app.post("/reset")
async def reset(request: ResetRequest = None) -> Dict[str, Any]:
    """
    Reset environment for new episode
    
    Args:
        task: Task name ("wealth_accumulation", "crisis_management", "portfolio_optimization")
        
    Returns:
        Initial observation
    """
    global env, current_task, episode_data
    
    if request:
        current_task = request.task
    
    logger.info(f"Resetting environment for task: {current_task}")
    
    # Initialize environment
    env = EnhancedFinLifeEnv(config=env_config, use_historical_data=True)
    obs = env.reset()
    
    # Reset episode tracking
    episode_data = {
        "task": current_task,
        "steps": 0,
        "rewards": [],
        "max_vix": 20.0,
        "peak_drawdown": 0.0,
        "recovery_ratio": 1.0,
        "used_tax_harvesting": False,
        "tax_loss_harvested": 0.0,
        "portfolio_value": obs.portfolio_value,
    }
    
    return _observation_to_dict(obs)


@app.post("/step")
async def step(request: StepRequest) -> Dict[str, Any]:
    """
    Execute action and advance environment
    
    Args:
        action: Action dictionary
        
    Returns:
        {
            "observation": {...},
            "reward": float,
            "done": bool,
            "info": {}
        }
    """
    global env, episode_data
    
    if env is None:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first.")
    
    try:
        # Convert dict to Action pydantic model
        action = Action(**request.action)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid action format: {str(e)}")
    
    # Execute step
    obs, reward, done, info = env.step(action)
    
    # Track episode data
    episode_data["steps"] += 1
    episode_data["rewards"].append(float(reward))
    episode_data["max_vix"] = max(episode_data["max_vix"], env.state.vix_level)
    episode_data["portfolio_value"] = obs.portfolio_value
    
    if action.tax_loss_harvest:
        episode_data["used_tax_harvesting"] = True
        episode_data["tax_loss_harvested"] += obs.realized_losses
    
    response = {
        "observation": _observation_to_dict(obs),
        "reward": float(reward),
        "done": done,
        "info": {
            "step": episode_data["steps"],
            "total_reward": sum(episode_data["rewards"]),
            "market_regime": env.state.market_regime,
        }
    }
    
    # Score episode if done
    if done:
        score = grade_task(
            current_task,
            _observation_to_dict(obs),
            episode_data
        )
        response["info"]["final_score"] = score
        logger.info(f"Episode done. Task: {current_task}, Score: {score:.3f}")
    
    return response


@app.get("/state")
async def get_state() -> Dict[str, Any]:
    """Get current observation"""
    global env
    
    if env is None:
        raise HTTPException(status_code=400, detail="Environment not initialized")
    
    obs = env._get_observation()
    return _observation_to_dict(obs)


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint - API info"""
    return {
        "name": "FinLife-OpenEnv API",
        "version": "2.0",
        "description": "OpenEnv-compliant financial life simulation environment",
        "endpoints": {
            "/status": "GET - Health check",
            "/reset": "POST - Initialize new episode",
            "/step": "POST - Take action and advance simulation",
            "/state": "GET - Get current observation",
            "/tasks": "GET - List available tasks",
            "/docs": "GET - Interactive API documentation (Swagger UI)"
        }
    }


@app.get("/tasks")
async def list_tasks() -> Dict[str, Any]:
    """List available tasks"""
    return {
        "tasks": [
            {
                "name": "wealth_accumulation",
                "difficulty": "easy",
                "description": "Accumulate wealth over 40-year career"
            },
            {
                "name": "crisis_management",
                "difficulty": "medium",
                "description": "Navigate market crash while preserving capital"
            },
            {
                "name": "portfolio_optimization",
                "difficulty": "hard",
                "description": "Multi-objective optimization (growth, risk, taxes, goals)"
            }
        ]
    }


def _observation_to_dict(obs) -> Dict[str, Any]:
    """Convert observation to serializable dict"""
    return {
        "age": obs.age,
        "month": obs.month,
        "income": float(obs.income),
        "expenses": float(obs.expenses),
        "savings": float(obs.savings),
        "net_worth": float(obs.net_worth),
        "equity": float(obs.equity),
        "debt": float(obs.debt),
        "cash": float(obs.cash),
        "portfolio_value": float(obs.portfolio_value),
        "goal_progress_summary": float(obs.goal_progress_summary),
        "risk_profile": obs.risk_profile,
        "dependents": obs.dependents,
        "job_stability": float(obs.job_stability),
        "health_factor": float(obs.health_factor),
        "is_bankrupt": obs.is_bankrupt,
        "market_regime": obs.market_regime,
        "vix_level": float(obs.vix_level),
        "inflation_rate": float(obs.inflation_rate),
        "interest_rate": float(obs.interest_rate),
        "diversification_score": float(obs.diversification_score),
        "realized_gains": float(obs.realized_gains),
        "realized_losses": float(obs.realized_losses),
    }


if __name__ == "__main__":
    logger.info("Starting FinLife-OpenEnv API server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
