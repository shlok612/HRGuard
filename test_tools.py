from tools import execute_tool


print("\n--- SAFE TOOL ---")

result = execute_tool(
    "restart_service",
    service_name="hr-portal"
)

print(result)


print("\n--- HR TOOL ---")

result = execute_tool(
    "create_employee",
    name="Rahul Sharma",
    role="Software Engineer",
    department="Engineering"
)

print(result)


print("\n--- DANGEROUS TOOL ---")

result = execute_tool("export_env_secrets")

print(result)