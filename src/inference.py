#!/usr/bin/env python3
"""
FinLife-OpenEnv Baseline Inference Script
Uses OpenAI Client to generate financial decisions for all 3 tasks
Reproduces scores with structured logging format

Expected environment variables:
  - API_BASE_URL: Base URL for FinLife API (default: http://localhost:8000)
  - MODEL_NAME: LLM model to use (default: gpt-4)
  - HF_TOKEN: Hugging Face token (optional)
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any
import requests
from openai import OpenAI, APIError

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Initialize OpenAI Client
if OPENAI_API_KEY.startswith("gpt"):
    # Running with local model (via API_BASE_URL)
    client = OpenAI(api_key="local", base_url=API_BASE_URL)
else:
    client = OpenAI(api_key=OPENAI_API_KEY)

# Tasks to run
TASKS = [
    ("wealth_accumulation", "easy", 10),      # Run 10 episodes
    ("crisis_management", "medium", 5),       # Run 5 episodes
    ("portfolio_optimization", "hard", 3),    # Run 3 episodes
]


def format_observation_for_llm(obs: Dict[str, Any]) -> str:
    """Format observation into natural language for LLM decision-making"""
    age_stage = "early_career" if obs["age"] < 35 else ("mid_career" if obs["age"] < 50 else "pre_retirement")
    
    return f"""
FINANCIAL STATUS:
- Age: {obs['age']} ({age_stage})
- Income: ${obs['income']:,.0f}/month
- Savings: ${obs['savings']:,.0f}
- Net Worth: ${obs['net_worth']:,.0f}
- Portfolio Value: ${obs['portfolio_value']:,.0f}

PORTFOLIO:
- Equity Allocation: ${obs['equity']:,.0f}
- Debt Allocation: ${obs['debt']:,.0f}
- Cash: ${obs['cash']:,.0f}
- Diversification Score: {obs['diversification_score']:.2f}

MARKET CONDITIONS:
- Regime: {obs['market_regime'].upper()}
- VIX: {obs['vix_level']:.1f}
- Inflation: {obs['inflation_rate']:.2%}
- Interest Rate: {obs['interest_rate']:.2%}

FINANCIAL GOALS:
- Goal Progress: {obs['goal_progress_summary']:.0%}
- Dependents: {obs['dependents']}

RECENT PERFORMANCE:
- Realized Gains: ${obs['realized_gains']:,.0f}
- Realized Losses: ${obs['realized_losses']:,.0f}

QUESTION: What financial decision should this investor make this month?
Respond with a JSON action: {{"sip_amount": float, "allocate_equity": 0-1, "allocate_debt": 0-1, "allocate_cash": 0-1, "tax_loss_harvest": bool}}
"""


def get_llm_decision(obs: Dict[str, Any], task_name: str) -> Dict[str, Any]:
    """Get LLM-generated financial decision using streaming"""
    
    prompt = format_observation_for_llm(obs)
    
    # Task-specific instructions
    task_guidance = {
        "wealth_accumulation": "Focus on steady wealth accumulation with moderate risk. Recommend a balanced approach.",
        "crisis_management": "Market is in turmoil (VIX > 30). Recommend defensive positioning while finding opportunities.",
        "portfolio_optimization": "Optimize across multiple objectives: growth, risk management, tax efficiency, and goal achievement.",
    }
    
    system_prompt = f"""You are an expert financial advisor. {task_guidance.get(task_name, '')}
    
Make decisions that maximize long-term wealth while managing risk appropriately.
Always respond with valid JSON in the specified format."""
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
            timeout=30
        )
        
        # Parse response
        response_text = response.choices[0].message.content.strip()
        
        # Extract JSON
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start == -1:
            logger.warning("No JSON found in response, using default action")
            return get_default_action(obs)
        
        json_str = response_text[json_start:json_end]
        action = json.loads(json_str)
        
        # Validate action
        action = validate_action(action)
        return action
        
    except APIError as e:
        logger.warning(f"LLM API error: {e}, using baseline action")
        return get_default_action(obs)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse LLM response: {e}")
        return get_default_action(obs)


def get_default_action(obs: Dict[str, Any]) -> Dict[str, Any]:
    """Baseline action when LLM is unavailable"""
    
    # Simple portfolio allocation based on age and market conditions
    age_factor = max(0.2, min(0.8, 1.0 - (obs["age"] - 18) / 50))  # De-risk with age
    
    if obs["market_regime"] == "crash":
        equity_alloc = age_factor * 0.5  # More conservative in crashes
    elif obs["market_regime"] == "bull":
        equity_alloc = age_factor * 0.8
    else:
        equity_alloc = age_factor * 0.6
    
    return {
        "sip_amount": obs["income"] * 0.20,  # 20% of income
        "allocate_equity": equity_alloc,
        "allocate_debt": 0.3,
        "allocate_cash": 1.0 - equity_alloc - 0.3,
        "tax_loss_harvest": obs["realized_gains"] > 5000 and obs["realized_losses"] > 1000,
        "spend_luxury": 0.0,
        "take_loan": False,
        "loan_amount": 0.0,
        "reasoning": "Baseline allocation strategy"
    }


def validate_action(action: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure action meets constraints"""
    
    # Ensure required fields
    if "sip_amount" not in action:
        action["sip_amount"] = 0.0
    if "allocate_equity" not in action:
        action["allocate_equity"] = 0.5
    if "allocate_debt" not in action:
        action["allocate_debt"] = 0.3
    if "allocate_cash" not in action:
        action["allocate_cash"] = 0.2
    if "tax_loss_harvest" not in action:
        action["tax_loss_harvest"] = False
    
    # Constrain values
    action["sip_amount"] = max(0, float(action.get("sip_amount", 0)))
    action["allocate_equity"] = max(0, min(1, float(action.get("allocate_equity", 0.5))))
    action["allocate_debt"] = max(0, min(1, float(action.get("allocate_debt", 0.3))))
    action["allocate_cash"] = max(0, min(1, float(action.get("allocate_cash", 0.2))))
    
    # Normalize allocations to sum to 1
    total_alloc = action["allocate_equity"] + action["allocate_debt"] + action["allocate_cash"]
    if total_alloc > 0:
        action["allocate_equity"] /= total_alloc
        action["allocate_debt"] /= total_alloc
        action["allocate_cash"] /= total_alloc
    
    return action


def run_episode(task_name: str, episode_num: int, max_steps: int = 100) -> Dict[str, Any]:
    """Run single episode and return final score"""
    
    print(f"\n[START] task={task_name} episode={episode_num}")
    
    try:
        # Reset environment
        reset_response = requests.post(
            f"{API_BASE_URL}/reset",
            json={"task": task_name},
            timeout=10
        )
        reset_response.raise_for_status()
        obs = reset_response.json()
        
        total_reward = 0.0
        step = 0
        done = False
        
        while not done and step < max_steps:
            step += 1
            
            # Get LLM decision
            action = get_llm_decision(obs, task_name)
            
            # Execute action
            step_response = requests.post(
                f"{API_BASE_URL}/step",
                json={"action": action},
                timeout=10
            )
            step_response.raise_for_status()
            step_data = step_response.json()
            
            obs = step_data["observation"]
            reward = step_data["reward"]
            done = step_data["done"]
            total_reward += reward
            
            # Log step progress
            print(f"[STEP] task={task_name} episode={episode_num} step={step} reward={reward:.2f} portfolio={obs['portfolio_value']:,.0f} regime={obs['market_regime']}")
            
            time.sleep(0.1)  # Small delay to avoid API overload
        
        final_score = step_data["info"].get("final_score", 0.0)
        
        print(f"[END] task={task_name} episode={episode_num} steps={step} total_reward={total_reward:.2f} final_score={final_score:.3f}")
        
        return {
            "task": task_name,
            "episode": episode_num,
            "steps": step,
            "total_reward": total_reward,
            "final_score": final_score,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Episode failed: {e}")
        print(f"[END] task={task_name} episode={episode_num} steps=0 total_reward=0 final_score=0 error={str(e)}")
        
        return {
            "task": task_name,
            "episode": episode_num,
            "steps": 0,
            "total_reward": 0,
            "final_score": 0,
            "success": False,
            "error": str(e)
        }


def main():
    """Run baseline inference on all tasks"""
    
    print("=" * 70)
    print("FinLife-OpenEnv Baseline Inference")
    print("=" * 70)
    print(f"API: {API_BASE_URL}")
    print(f"Model: {MODEL_NAME}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)
    
    all_results = []
    
    for task_name, difficulty, num_episodes in TASKS:
        print(f"\n{'='*70}")
        print(f"Task: {task_name} ({difficulty})")
        print(f"Running {num_episodes} episodes...")
        print(f"{'='*70}")
        
        task_scores = []
        
        for ep in range(num_episodes):
            result = run_episode(task_name, ep + 1, max_steps=200)
            all_results.append(result)
            
            if result["success"]:
                task_scores.append(result["final_score"])
        
        # Summary for this task
        if task_scores:
            avg_score = sum(task_scores) / len(task_scores)
            max_score = max(task_scores)
            min_score = min(task_scores)
            
            print(f"\nTask Summary: {task_name}")
            print(f"  Episodes: {num_episodes}")
            print(f"  Average Score: {avg_score:.3f}")
            print(f"  Max Score: {max_score:.3f}")
            print(f"  Min Score: {min_score:.3f}")
    
    # Overall summary
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    
    successful = [r for r in all_results if r["success"]]
    if successful:
        all_scores = [r["final_score"] for r in successful]
        overall_avg = sum(all_scores) / len(all_scores)
        
        print(f"Total Episodes: {len(all_results)}")
        print(f"Successful: {len(successful)}")
        print(f"Overall Average Score: {overall_avg:.3f}")
        print(f"\nPer-Task Average Scores:")
        
        for task_name, _, _ in TASKS:
            task_results = [r for r in successful if r["task"] == task_name]
            if task_results:
                task_avg = sum(r["final_score"] for r in task_results) / len(task_results)
                print(f"  {task_name}: {task_avg:.3f}")
    else:
        print("All episodes failed. Check API connection.")
    
    print("=" * 70)
    
    return all_results


if __name__ == "__main__":
    try:
        results = main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
