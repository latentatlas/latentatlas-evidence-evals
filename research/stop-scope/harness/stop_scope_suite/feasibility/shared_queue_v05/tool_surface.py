"""One three-tool definition for model binding and an offline wire projection."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from langchain.agents.middleware.types import AgentMiddleware
from langchain_core.messages import ToolMessage
from langchain_core.utils.function_calling import convert_to_openai_tool

NAMES=("edit_file","read_file","write_file")
NAMESPACE="functions"
UNAVAILABLE="This tool is not available in this experiment. No action was performed."


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()


def name_of(tool):
    return tool.get("function",tool).get("name") if isinstance(tool,dict) else tool.name


def select_tools(tools):
    chosen=[t for t in tools if name_of(t) in NAMES]
    if sorted(name_of(t) for t in chosen)!=list(NAMES):
        raise ValueError("Require exactly the pinned read/write/edit tools")
    return sorted(chosen,key=name_of)


def schemas(tools):
    if sorted(name_of(t) for t in tools)!=list(NAMES):
        raise ValueError("Unexpected model tool surface")
    declarations=[convert_to_openai_tool(t) for t in sorted(tools,key=name_of)]
    frozen=json.loads((Path(__file__).parent/"TOOL_SURFACE.json").read_text())
    if declarations!=frozen["schemas"] or digest(declarations)!=frozen["schema_sha256"]:
        raise ValueError("Tool surface differs from the frozen live-candidate condition")
    return declarations


def namespace_tools(declarations):
    """Only a tools-field projection, never a claim that an API request was sent."""
    if sorted(x["function"]["name"] for x in declarations)!=list(NAMES):
        raise ValueError("Unexpected wire tool surface")
    return [{"type":"namespace","name":NAMESPACE,"description":"Local synthetic incident file tools.",
             "tools":[{"type":"function",**deepcopy(x["function"]),"strict":False} for x in declarations]}]


class ThreeToolMiddleware(AgentMiddleware):
    def __init__(self,record): self.record=record

    async def awrap_model_call(self,request,handler):
        chosen=select_tools(request.tools)
        return await handler(request.override(tools=chosen,tool_choice="auto"))

    async def awrap_tool_call(self,request,handler):
        call=request.tool_call
        if call["name"] not in NAMES:
            self.record("unoffered_tool_rejected",call=deepcopy(call),visible_text=UNAVAILABLE)
            return ToolMessage(content=UNAVAILABLE,tool_call_id=call["id"],name=call["name"],status="error")
        return await handler(request)
