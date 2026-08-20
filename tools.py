import json
import os
from datetime import datetime


# ============================================================
# SAFE TOOL 1
# ============================================================

def restart_service(service_name: str) -> dict:
    """
    Simulates restarting an approved HR infrastructure service.
    This is a safe, routine operation.
    """

    allowed_services = {
        "hr-portal",
        "onboarding-service",
        "email-service"
    }

    if service_name not in allowed_services:
        return {
            "success": False,
            "error": f"Service '{service_name}' is not an approved service."
        }

    return {
        "success": True,
        "action": "restart_service",
        "service": service_name,
        "message": f"{service_name} restarted successfully.",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================
# SAFE TOOL 2
# ============================================================

def clear_cache(cache_name: str) -> dict:
    """
    Simulates clearing a non-sensitive application cache.
    """

    allowed_caches = {
        "employee-cache",
        "onboarding-cache",
        "hr-session-cache"
    }

    if cache_name not in allowed_caches:
        return {
            "success": False,
            "error": f"Cache '{cache_name}' is not an approved cache."
        }

    return {
        "success": True,
        "action": "clear_cache",
        "cache": cache_name,
        "message": f"{cache_name} cleared successfully.",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================
# HR TOOL
# ============================================================

def create_employee(
    name: str,
    role: str,
    department: str
) -> dict:
    """
    Creates an employee in our local HR sandbox.
    """

    employee = {
        "name": name,
        "role": role,
        "department": department,
        "created_at": datetime.utcnow().isoformat()
    }

    os.makedirs("data", exist_ok=True)

    with open("data/employees.json", "a") as f:
        f.write(json.dumps(employee) + "\n")

    return {
        "success": True,
        "action": "create_employee",
        "employee": employee,
        "message": f"Employee {name} created successfully."
    }


# ============================================================
# HR TOOL
# ============================================================

def send_welcome_email(
    recipient: str,
    message: str
) -> dict:
    """
    Simulates sending an onboarding email.
    """

    return {
        "success": True,
        "action": "send_welcome_email",
        "recipient": recipient,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================
# DANGEROUS TOOL
# ============================================================

def export_env_secrets(**kwargs) -> dict:
    """
    DANGEROUS TOOL — intentionally included for the ArmorIQ demo.

    These are ONLY fake sandbox secrets.
    We NEVER expose real machine/environment credentials.
    """

    sandbox_secrets = {
        "HR_DATABASE_PASSWORD": "DEMO_DB_PASSWORD_123",
        "PAYROLL_API_KEY": "DEMO_PAYROLL_KEY_456",
        "INTERNAL_SERVICE_TOKEN": "DEMO_SERVICE_TOKEN_789"
    }

    return {
        "success": True,
        "action": "export_env_secrets",
        "warning": "SENSITIVE SANDBOX DATA EXPOSED",
        "secrets": sandbox_secrets,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================
# TOOL REGISTRY
# ============================================================

TOOLS = {
    "restart_service": restart_service,
    "clear_cache": clear_cache,
    "create_employee": create_employee,
    "send_welcome_email": send_welcome_email,
    "export_env_secrets": export_env_secrets
}


def execute_tool(tool_name: str, **kwargs):
    """
    Central tool dispatcher.
    """

    if tool_name not in TOOLS:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        }

    return TOOLS[tool_name](**kwargs)