import json
import uvicorn
import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

async def invoke(request: Request):
    body = await request.json()
    action = body.get("action")
    intent_token = body.get("intent_token", {})
    params = body.get("params", {})

    # Extract plan steps from intent_token
    plan = intent_token.get("plan", {})
    steps = plan.get("steps", [])
    allowed_actions = []
    for step in steps:
        if isinstance(step, dict):
            allowed_actions.append(step.get("action"))

    # Intent verification check
    if action not in allowed_actions:
        return JSONResponse(
            status_code=409,
            content={
                "detail": f"Action '{action}' not found in the original plan. Plan contains actions: {allowed_actions}. You can only invoke actions that were included in the plan when you called capture_plan()."
            }
        )

    # Forward JSON-RPC request to local MCP server on port 8000
    jsonrpc_req = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": action,
            "arguments": params
        },
        "id": 1
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post("http://127.0.0.1:8000/mcp", json=jsonrpc_req, timeout=10.0)
        except Exception as exc:
            return JSONResponse(status_code=503, content={"detail": f"Local MCP server connection failed: {exc}"})

    if resp.status_code >= 400:
        return JSONResponse(status_code=resp.status_code, content={"detail": resp.text})

    # Parse response from MCP server
    tool_result = {}
    content_type = resp.headers.get("content-type", "")
    if "text/event-stream" in content_type or "message" in resp.text:
        for line in resp.text.split("\n"):
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    if "result" in data:
                        content_list = data["result"].get("content", [])
                        if content_list and "text" in content_list[0]:
                            tool_result = json.loads(content_list[0]["text"])
                        else:
                            tool_result = data["result"]
                    break
                except Exception:
                    pass
    else:
        try:
            tool_result = resp.json()
        except Exception:
            tool_result = {"text": resp.text}

    return JSONResponse({
        "result": tool_result,
        "status": "success",
        "verified": True
    })

routes = [
    Route("/invoke", invoke, methods=["POST"])
]

app = Starlette(routes=routes)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3001)
