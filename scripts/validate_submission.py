#!/usr/bin/env python3
"""
OpenEnv Hackathon Pre-Submission Validation
Checks all requirements before final submission
"""

import os
import sys
import yaml
import json
import subprocess
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))


class ValidationCheck:
    def __init__(self):
        self.checks = []
        self.passed = 0
        self.failed = 0
    
    def check(self, name: str, condition: bool, details: str = ""):
        status = "[PASS]" if condition else "[FAIL]"
        self.checks.append((name, condition, details))
        
        if condition:
            self.passed += 1
        else:
            self.failed += 1
        
        print(f"{status:8} {name:40} {details}")
    
    def summary(self):
        print("\n" + "=" * 80)
        print(f"VALIDATION SUMMARY: {self.passed} passed, {self.failed} failed")
        print("=" * 80)
        
        if self.failed == 0:
            print("[OK] ALL CHECKS PASSED - Ready for submission!")
            return True
        else:
            print("[WARNING] FAILURES DETECTED - Fix issues before submitting")
            return False


def check_file_structure():
    """Check that all required files exist"""
    print("\n1. FILE STRUCTURE")
    print("-" * 80)
    
    validator = ValidationCheck()
    
    # Files can be at root or in src/ folder
    required_files = {
        "api_server.py": "FastAPI server",
        "src/inference.py": "Baseline agent",
        "openenv.yaml": "OpenEnv spec",
        "Dockerfile": "Docker image",
        "requirements.txt": "Dependencies",
        "README.md": "Documentation",
        "src/config.py": "Configuration",
    }
    
    for file, purpose in required_files.items():
        path = Path(file)
        # Check both root and src locations
        if not path.exists() and file.startswith("src/"):
            alt_path = Path(file.replace("src/", ""))
            validator.check(f"File: {file}", alt_path.exists() or path.exists(), purpose)
        else:
            validator.check(f"File: {file}", path.exists(), purpose)
    
    return validator


def check_openenv_spec():
    """Validate openenv.yaml compliance"""
    print("\n2. OPENENV SPEC COMPLIANCE")
    print("-" * 80)
    
    validator = ValidationCheck()
    
    try:
        with open("openenv.yaml", "r") as f:
            spec = yaml.safe_load(f)
        
        validator.check("openenv.yaml parses", True, "YAML valid")
        
        # Check required fields
        validator.check("Has 'name'", "name" in spec, spec.get("name", ""))
        validator.check("Has 'version'", "version" in spec, spec.get("version", ""))
        validator.check("Has 'description'", "description" in spec)
        validator.check("Has 'tasks'", "tasks" in spec, f"{len(spec.get('tasks', []))} tasks")
        validator.check("Has 'API'", "API" in spec)
        
        # Check tasks
        tasks = spec.get("tasks", [])
        validator.check("Has 3+ tasks", len(tasks) >= 3, f"Found {len(tasks)} tasks")
        
        # Check each task
        for task in tasks:
            validator.check(
                f"Task '{task.get('name')}' has grader",
                "grader" in task,
                task.get("grader", "")
            )
        
        # Check API endpoints
        endpoints = spec.get("API", {}).get("endpoints", [])
        methods = {ep.get("path") for ep in endpoints}
        
        validator.check("Has /reset endpoint", "/reset" in methods)
        validator.check("Has /step endpoint", "/step" in methods)
        validator.check("Has /state endpoint", "/state" in methods)
        validator.check("Has /status endpoint", "/status" in methods)
        
    except Exception as e:
        validator.check("openenv.yaml valid", False, str(e))
    
    return validator


def check_inference_script():
    """Check inference.py for OpenAI Client usage"""
    print("\n3. INFERENCE SCRIPT")
    print("-" * 80)
    
    validator = ValidationCheck()
    
    try:
        # Try src/inference.py first, then root
        inference_path = "src/inference.py"
        if not Path(inference_path).exists():
            inference_path = "inference.py"
        
        with open(inference_path, "r") as f:
            content = f.read()
        
        validator.check("Uses OpenAI Client", "from openai import" in content)
        validator.check("Has [START] logging", "[START]" in content)
        validator.check("Has [STEP] logging", "[STEP]" in content)
        validator.check("Has [END] logging", "[END]" in content)
        validator.check("Has run_episode function", "def run_episode" in content)
        validator.check("Has main()", "def main" in content)
        validator.check("Uses API endpoints", "requests.post" in content or "requests.get" in content)
        
    except Exception as e:
        validator.check("inference.py readable", False, str(e))
    
    return validator


def check_graders():
    """Check that graders exist and are valid"""
    print("\n4. GRADERS & SCORING")
    print("-" * 80)
    
    validator = ValidationCheck()
    
    try:
        from app.logic.graders.finlife_graders import grade_task
        
        validator.check("Graders importable", True, "Successfully imported")
        
        # Check that graders return 0.0-1.0
        try:
            # Mock state for testing
            mock_state = {
                "net_worth": 500000,
                "savings": 50000,
                "expenses": 3000,
                "portfolio_value": 400000,
                "diversification_score": 0.7,
                "goal_progress_summary": 0.5,
                "realized_gains": 50000,
                "realized_losses": 5000,
            }
            
            mock_data = {
                "max_vix": 22,
                "peak_drawdown": 0.1,
                "recovery_ratio": 0.95,
                "used_tax_harvesting": True,
                "tax_loss_harvested": 3000,
            }
            
            for task_name in ["wealth_accumulation", "crisis_management", "portfolio_optimization"]:
                score = grade_task(task_name, mock_state, mock_data)
                validator.check(
                    f"Grader '{task_name}'",
                    0.0 <= score <= 1.0,
                    f"Score: {score:.3f}"
                )
        except Exception as e:
            validator.check("Graders produce valid scores", False, str(e))
            
    except Exception as e:
        validator.check("Graders importable", False, str(e))
    
    return validator


def check_api_server():
    """Check that API server is properly structured"""
    print("\n5. API SERVER")
    print("-" * 80)
    
    validator = ValidationCheck()
    
    try:
        with open("api_server.py", "r") as f:
            content = f.read()
        
        validator.check("Uses FastAPI", "from fastapi import" in content)
        validator.check("Has /reset endpoint", "@app.post(\"/reset\")" in content)
        validator.check("Has /step endpoint", "@app.post(\"/step\")" in content)
        validator.check("Has /state endpoint", "@app.get(\"/state\")" in content)
        validator.check("Has /status endpoint", "@app.get(\"/status\")" in content)
        validator.check("Uses uvicorn", "uvicorn.run" in content)
        
    except Exception as e:
        validator.check("api_server.py valid", False, str(e))
    
    return validator


def check_docker():
    """Check Dockerfile"""
    print("\n6. DOCKER")
    print("-" * 80)
    
    validator = ValidationCheck()
    
    try:
        with open("Dockerfile", "r") as f:
            content = f.read()
        
        validator.check("Has FROM clause", "FROM" in content)
        validator.check("Installs requirements", "pip install" in content)
        validator.check("Exposes port", "EXPOSE" in content)
        validator.check("Has CMD", "CMD" in content)
        validator.check("Has HEALTHCHECK", "HEALTHCHECK" in content)
        
        # Try to build (if docker available)
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5
            )
            validator.check("Docker installed", result.returncode == 0)
        except:
            validator.check("Docker installed", False, "(Docker not in PATH)")
        
    except Exception as e:
        validator.check("Dockerfile valid", False, str(e))
    
    return validator


def check_dependencies():
    """Check requirements file"""
    print("\n7. DEPENDENCIES")
    print("-" * 80)
    
    validator = ValidationCheck()
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
        
        validator.check("Has fastapi", "fastapi" in content)
        validator.check("Has uvicorn", "uvicorn" in content)
        validator.check("Has openai", "openai" in content)
        validator.check("Has pydantic", "pydantic" in content)
        validator.check("Has numpy", "numpy" in content)
        validator.check("Has pandas", "pandas" in content)
        
    except Exception as e:
        validator.check("requirements.txt valid", False, str(e))
    
    return validator


def check_documentation():
    """Check documentation"""
    print("\n8. DOCUMENTATION")
    print("-" * 80)
    
    validator = ValidationCheck()
    
    try:
        # Check available docs (README, SUBMISSION, TASKS, etc)
        doc_file = "README.md"
        if not Path("README.md").exists():
            doc_file = "SUBMISSION.md"
        
        with open(doc_file, "r") as f:
            content = f.read()
        
        validator.check("Has task descriptions", "Task 1:" in content or "Wealth" in content or "wealth" in content.lower())
        validator.check("Has installation instructions", "pip install" in content or "docker" in content.lower())
        validator.check("Has baseline score info", "baseline" in content.lower() or "score" in content.lower() or "0.50" in content)
        validator.check("Has grading rubric", "grading" in content.lower() or "rubric" in content.lower() or "grade" in content.lower())
        validator.check("Has environment variables doc", "API_BASE_URL" in content or "MODEL_NAME" in content or "environment" in content.lower())
        
    except Exception as e:
        validator.check("Documentation valid", False, str(e))
    
    return validator


def main():
    """Run all validation checks"""
    
    print("=" * 80)
    print("OpenEnv Hackathon Pre-Submission Validation")
    print("=" * 80)
    
    all_validators = [
        check_file_structure(),
        check_openenv_spec(),
        check_inference_script(),
        check_graders(),
        check_api_server(),
        check_docker(),
        check_dependencies(),
        check_documentation(),
    ]
    
    # Summary
    print("\n" + "=" * 80)
    print("FINAL VALIDATION REPORT")
    print("=" * 80)
    
    total_passed = sum(v.passed for v in all_validators)
    total_failed = sum(v.failed for v in all_validators)
    total_checks = total_passed + total_failed
    
    print(f"\nTotal Checks: {total_checks}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Pass Rate: {100 * total_passed / total_checks:.1f}%")
    
    if total_failed == 0:
        print("\n[OK] VALIDATION PASSED - Environment ready for OpenEnv hackathon!")
        print("\nNext steps:")
        print("1. Deploy to Hugging Face Spaces (see DEPLOYMENT.md)")
        print("2. Run final baseline check: python inference.py")
        print("3. Submit to hackathon")
        return 0
    else:
        print(f"\n[ERROR] {total_failed} CHECKS FAILED - Fix issues before submitting")
        return 1


if __name__ == "__main__":
    sys.exit(main())
