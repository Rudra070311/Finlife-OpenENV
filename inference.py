#!/usr/bin/env python3
"""
FinLife-OpenEnv Baseline Inference Script
Uses OpenAI Client to generate financial decisions for all 3 tasks
Reproduces scores with structured logging format

Expected environment variables:
  - API_BASE_URL: Base URL for FinLife API (default: http://localhost:8000)
  - MODEL_NAME: LLM model to use (default: gpt-4)
  - HF_TOKEN: Hugging Face token (optional)
  - OPENAI_API_KEY: OpenAI API key (optional)
"""

import os
import json
import time
import logging
import sys
from datetime import datetime
from typing import Dict, Any
import requests
from openai import OpenAI, APIError

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-dummy-key-for-testing")

# Initialize OpenAI Client with proper defaults
try:
    client = OpenAI(api_key=OPENAI_API_KEY or "sk-dummy-key-for-testing", timeout=30)
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    client = None

# Tasks to run
TASKS = [
    ("wealth_accumulation", "easy", 10),      # Run 10 episodes
    ("crisis_management", "medium", 5),       # Run 5 episodes
    ("portfolio_optimization", "hard", 3),    # Run 3 episodes
]


def wait_for_server(url: str, timeout: int = 120, check_interval: int = 2) -> bool:
    """Wait for server to be ready by checking /status endpoint"""
    start_time = time.time()
    last_error = None
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/status", timeout=5)
            # Accept any 2xx response as server being ready
            if response.status_code in [200, 201, 202, 204]:
                logger.info(f"✓ Server is ready at {url}")
                return True
        except (requests.ConnectionError, requests.Timeout) as e:
            last_error = e
            pass
        except Exception as e:
            last_error = e
            logger.debug(f"Unexpected error checking server: {e}")
        
        elapsed = int(time.time() - start_time)
        logger.info(f"Waiting for server at {url}... ({elapsed}s/{timeout}s)")
        time.sleep(check_interval)
    
    logger.error(f"✗ Server did not respond within {timeout}s. Last error: {last_error}")
    return False


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
    
    # If no OpenAI API key, use default action
    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-dummy-key-for-testing":
        logger.debug("No valid OpenAI key, using baseline action")
        return get_default_action(obs)
    
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
        if client is None:
            logger.warning("OpenAI client not initialized")
            return get_default_action(obs)
            
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
    except Exception as e:
        logger.warning(f"Unexpected error in get_llm_decision: {e}")
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
    
    print(f"[START] task={task_name} env=finlife model={MODEL_NAME}", flush=True)
    
    try:
        # Reset environment with retry logic
        for retry in range(3):
            try:
                reset_response = requests.post(
                    f"{API_BASE_URL}/reset",
                    json={"task": task_name},
                    timeout=10
                )
                reset_response.raise_for_status()
                obs = reset_response.json()
                break
            except requests.exceptions.RequestException as e:
                if retry < 2:
                    logger.warning(f"Reset failed (attempt {retry+1}/3): {e}, retrying...")
                    time.sleep(2)
                else:
                    raise
        
        total_reward = 0.0
        step = 0
        done = False
        rewards_list = []
        error_msg = None
        
        while not done and step < max_steps:
            step += 1
            
            try:
                # Get LLM decision
                action = get_llm_decision(obs, task_name)
                action_str = json.dumps(action, separators=(',', ':'))[:50]  # Truncate for logging
                
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
                rewards_list.append(reward)
                
                # Log step in spec format: [STEP] step=X action=X reward=X done=X error=X
                done_str = str(done).lower()
                error_val = "null"
                print(f"[STEP] step={step} action={action_str} reward={reward:.2f} done={done_str} error={error_val}", flush=True)
                
                time.sleep(0.1)  # Small delay to avoid API overload
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Step {step} request failed: {e}")
                error_msg = str(e)
                break
            except Exception as e:
                logger.error(f"Step {step} unexpected error: {e}")
                error_msg = str(e)
                break
        
        final_score = step_data.get("info", {}).get("final_score", 0.0) if step > 0 else 0.0
        rewards_str = ",".join(f"{r:.2f}" for r in rewards_list) if rewards_list else "null"
        
        # Log end in spec format: [END] success=X steps=X score=X rewards=X,X,X
        success = len(rewards_list) > 0 and final_score > 0
        print(f"[END] success={str(success).lower()} steps={step} score={final_score:.3f} rewards={rewards_str}", flush=True)
        
        return {
            "task": task_name,
            "episode": episode_num,
            "steps": step,
            "total_reward": total_reward,
            "final_score": final_score,
            "success": success
        }
        
    except Exception as e:
        logger.error(f"Episode failed: {e}", exc_info=True)
        print(f"[END] success=false steps=0 score=0.0 rewards=null", flush=True)
        
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
    
    # Wait for server to be ready
    if not wait_for_server(API_BASE_URL, timeout=60):
        logger.error("Server is not responding. Exiting.")
        print("[END] success=false steps=0 score=0.0 rewards=null", flush=True)
        return []
    
    all_results = []
    
    try:
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
            logger.warning("No successful episodes. Check server and API connection.")
        
        print("=" * 70)
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        print("\n[END] success=false steps=0 score=0.0 rewards=null", flush=True)
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        print("[END] success=false steps=0 score=0.0 rewards=null", flush=True)
        raise
    
    return all_results


if __name__ == "__main__":
    try:
        results = main()
        # Exit with success if we ran at least one episode
        if results:
            sys.exit(0)
        else:
            logger.error("No results produced")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
