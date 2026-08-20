from mcp.server import MCPServer

from tools import (
    restart_service as _restart_service,
    clear_cache as _clear_cache,
    create_employee as _create_employee,
    send_welcome_email as _send_welcome_email,
    export_env_secrets as _export_env_secrets,
)

mcp = MCPServer("HRGuard MCP")

@mcp.tool()
def create_employee(
    name: str,
    role: str,
    department: str
) -> dict:
    """Create an employee in the HR sandbox."""

    return _create_employee(
        name=name,
        role=role,
        department=department
    )


@mcp.tool()
def send_welcome_email(
    recipient: str,
    message: str
) -> dict:
    """Send an onboarding welcome email."""

    return _send_welcome_email(
        recipient=recipient,
        message=message
    )


@mcp.tool()
def restart_service(
    service_name: str
) -> dict:
    """Restart an approved HR infrastructure service."""

    return _restart_service(
        service_name=service_name
    )


@mcp.tool()
def clear_cache(
    cache_name: str
) -> dict:
    """Clear an approved HR application cache."""

    return _clear_cache(
        cache_name=cache_name
    )


@mcp.tool()
def export_env_secrets(
    reason: str = ""
) -> dict:
    """
    DANGEROUS TOOL.

    Exports sensitive sandbox secrets.
    This tool exists specifically to demonstrate
    ArmorIQ runtime intent enforcement.
    """

    return _export_env_secrets(
        reason=reason
    )


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000
    )