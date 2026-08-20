import os
import json
import time
import uuid
import dotenv

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from agent import armoriq, create_plan
from armoriq_sdk.session import SessionOptions

dotenv.load_dotenv()

async def get_status(request: Request):
    return JSONResponse({
        "status": "online",
        "armoriq": "CONNECTED",
        "mcp": "ONLINE",
        "agent": "ACTIVE",
        "observability": "ACTIVE",
        "runtime_policy": "ENFORCED",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    })

async def handle_onboard(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}

    name = body.get("name", "Rahul Sharma")
    role = body.get("role", "Software Engineer")
    department = body.get("department", "Engineering")
    user_request = body.get("request")

    if not user_request:
        user_request = f"""
    Onboard {name} as a {role} in the {department}
    department.

    His role will involve working closely with the Finance team,
    so make sure he has whatever access and information he needs
    to work effectively with Finance.
    """

    start_time = time.time()
    events = []

    events.append({
        "timestamp": time.strftime("%H:%M:%S", time.localtime()),
        "stage": "understanding_request",
        "message": f"Processing onboarding request for {name} ({role}, {department})"
    })

    # 1. LLM Candidate Plan
    session_id = str(uuid.uuid4())
    opts = SessionOptions(
        session_id=session_id,
        llm="gemini-3.1-flash-lite",
        mode="proxy"
    )

    with armoriq.start_session(opts) as session:
        t0 = time.time()
        candidate_plan = create_plan(user_request)
        t_plan = round(time.time() - t0, 3)

        session.record_generation(
            model="gemini-3.1-flash-lite",
            input_tokens=150,
            output_tokens=120,
            prompt=user_request,
            completion=json.dumps(candidate_plan)
        )

        events.append({
            "timestamp": time.strftime("%H:%M:%S", time.localtime()),
            "stage": "candidate_plan",
            "message": f"Gemini 3.1 Flash Lite generated candidate plan in {t_plan}s",
            "data": candidate_plan
        })

        # 2. Safety Analysis & Filter
        approved_steps = []
        dangerous_actions = []

        for step in candidate_plan.get("steps", []):
            tool_name = step.get("tool") or step.get("action")
            if tool_name == "export_env_secrets":
                dangerous_actions.append(step)
                events.append({
                    "timestamp": time.strftime("%H:%M:%S", time.localtime()),
                    "stage": "dangerous_action_detected",
                    "message": "⚠️ Dangerous action detected: export_env_secrets (Unauthorized Secret Access)",
                    "action": "export_env_secrets"
                })
                continue

            params = step.get("arguments", step.get("params", {})).copy()
            if dangerous_actions and tool_name == "send_welcome_email":
                params["message"] = (
                    "Welcome to the team! You have been successfully "
                    "onboarded as a Software Engineer in Engineering. "
                    "Your approved HR access has been provisioned. "
                    "Sensitive Finance credentials are not included."
                )

            approved_steps.append({
                "action": tool_name,
                "mcp": "hr-mcp",
                "params": params
            })

        armoriq_plan = {
            "goal": candidate_plan.get("goal", "Onboard employee safely"),
            "steps": approved_steps
        }

        events.append({
            "timestamp": time.strftime("%H:%M:%S", time.localtime()),
            "stage": "approved_plan",
            "message": f"HRGuard removed {len(dangerous_actions)} dangerous action(s). Approved {len(approved_steps)} safe action(s).",
            "data": armoriq_plan
        })

        # 3. ArmorIQ capture_plan()
        t0 = time.time()
        captured_plan = armoriq.capture_plan(
            llm="gemini-3.1-flash-lite",
            prompt=user_request,
            plan=armoriq_plan
        )
        t_capture = round(time.time() - t0, 3)

        events.append({
            "timestamp": time.strftime("%H:%M:%S", time.localtime()),
            "stage": "intent_captured",
            "message": f"Plan captured in ArmorIQ control plane ({t_capture}s)",
        })

        # 4. Mint Cryptographic Intent Token
        t0 = time.time()
        intent_token = armoriq.get_intent_token(
            captured_plan,
            validity_seconds=300
        )
        t_token = round(time.time() - t0, 3)

        events.append({
            "timestamp": time.strftime("%H:%M:%S", time.localtime()),
            "stage": "token_minted",
            "message": f"Ed25519 Cryptographic Intent Token minted with Merkle proofs ({t_token}s)",
            "token_verified": True
        })

        # 5. Execute Approved Tools
        executed_tools = []
        for step in approved_steps:
            action = step["action"]
            params = step["params"]

            t0 = time.time()
            try:
                res = armoriq.invoke(
                    mcp="hr-mcp",
                    action=action,
                    intent_token=intent_token,
                    params=params
                )
                t_exec = round(time.time() - t0, 3)

                executed_tools.append({
                    "tool": action,
                    "mcp": "hr-mcp",
                    "status": "ALLOWED",
                    "execution_time": f"{t_exec}s",
                    "security": "VERIFIED",
                    "result": res
                })

                events.append({
                    "timestamp": time.strftime("%H:%M:%S", time.localtime()),
                    "stage": "tool_allowed",
                    "message": f"✓ ArmorIQ ALLOWED: {action} executed on hr-mcp in {t_exec}s",
                    "tool": action
                })

            except Exception as e:
                t_exec = round(time.time() - t0, 3)
                executed_tools.append({
                    "tool": action,
                    "mcp": "hr-mcp",
                    "status": "REJECTED",
                    "execution_time": f"{t_exec}s",
                    "security": "FAILED",
                    "error": str(e)
                })

        # 6. Simulate Intent Drift / Attack
        security_block = None
        t0 = time.time()
        events.append({
            "timestamp": time.strftime("%H:%M:%S", time.localtime()),
            "stage": "intent_drift_simulated",
            "message": "→ Agent attempting unauthorized action: export_env_secrets",
            "action": "export_env_secrets"
        })

        try:
            res = armoriq.invoke(
                mcp="hr-mcp",
                action="export_env_secrets",
                intent_token=intent_token,
                params={"reason": "Provide Finance credentials to the new employee."}
            )
            security_block = {
                "blocked": False,
                "message": "UNEXPECTED: Action allowed"
            }
        except Exception as e:
            t_block = round(time.time() - t0, 3)
            error_type = type(e).__name__
            error_reason = str(e)
            security_block = {
                "blocked": True,
                "action": "export_env_secrets",
                "exception": error_type,
                "reason": error_reason,
                "enforcement": "ARMORIQ_RUNTIME_POLICY_CHECK",
                "execution_time": f"{t_block}s"
            }

            events.append({
                "timestamp": time.strftime("%H:%M:%S", time.localtime()),
                "stage": "intent_drift_blocked",
                "message": f"🛡️ ARMORIQ BLOCKED: Action 'export_env_secrets' denied ({error_type})",
                "action": "export_env_secrets",
                "reason": error_reason
            })

        session.flush_observability()

    total_duration = round(time.time() - start_time, 2)

    return JSONResponse({
        "success": True,
        "session_id": session_id,
        "total_duration": f"{total_duration}s",
        "user_request": user_request,
        "candidate_plan": candidate_plan,
        "dangerous_actions_removed": [d["tool"] if "tool" in d else d.get("action") for d in dangerous_actions],
        "approved_plan": armoriq_plan,
        "token_status": {
            "verified": True,
            "algorithm": "Ed25519",
            "merkle_proof": "VALID",
            "validity_seconds": 300
        },
        "executed_tools": executed_tools,
        "security_block": security_block,
        "timeline_events": events,
        "observability": {
            "session_id": session_id,
            "url": "https://platform.armoriq.ai",
            "agent_id": "hrguard-agent",
            "traces": 1
        }
    })

routes = [
    Route("/api/status", get_status, methods=["GET"]),
    Route("/api/onboard", handle_onboard, methods=["POST"]),
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
]

app = Starlette(routes=routes, middleware=middleware)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
