# app/services/langgraph.py
from __future__ import annotations

import json
import time
from typing import Annotated, List

from bson import ObjectId
from langchain.chat_models import init_chat_model
from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from app.config import settings
from app.db.repositories import save_message
from app.services.mcp import get_mcp_tools
from app.tools.weather_tool import get_weather_forecast


# NEW: the graph state explicitly includes uid
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    uid: str
    conversation_id: ObjectId


def build_prompt(
    new_user_text: str, history_docs: list[dict] = []
) -> List[BaseMessage]:
    msgs: List[BaseMessage] = [SystemMessage(content=settings.SYSTEM_PROMPT)]
    for d in history_docs:
        if d.get("role") == "user":
            msgs.append(HumanMessage(content=d.get("text", "")))
        elif d.get("role") == "assistant":
            msgs.append(AIMessage(content=d.get("text", "")))
    msgs.append(HumanMessage(content=new_user_text))
    return msgs


_agent_graph = None


async def get_agent_graph():
    global _agent_graph
    if _agent_graph is not None:
        return _agent_graph

    model = init_chat_model(settings.GEMINI_MODEL, api_key=settings.GOOGLE_API_KEY)

    try:
        tools: List[BaseTool] = await get_mcp_tools()
    except Exception:
        tools = []

    tools = tools + [get_weather_forecast]

    tools_by_name = {t.name: t for t in tools}
    model_with_tools = model.bind_tools(tools)

    async def call_model(state: AgentState):
        resp = await model_with_tools.ainvoke(state["messages"])
        return {"messages": [resp]}  # uid is preserved automatically

    async def call_tools(state: AgentState):
        uid = state["uid"]  # ← now always present
        conversation_id = state["conversation_id"]

        last = state["messages"][-1]
        if not isinstance(last, AIMessage) or not getattr(last, "tool_calls", None):
            return {"messages": []}

        tool_msgs: List[ToolMessage] = []
        for tc in last.tool_calls:
            name = tc.get("name")
            args = tc.get("args") or {}
            tool_call_id = tc.get("id")
            tool = tools_by_name.get(name)

            start = time.perf_counter()
            error_txt = None
            output = None
            try:
                if tool is None:
                    raise RuntimeError(f"Tool '{name}' not found.")
                result = await tool.ainvoke(args)
                output = result
            except Exception as e:
                error_txt = str(e)
                output = {"error": error_txt}
            elapsed_ms = int((time.perf_counter() - start) * 1000)

            def _txt(x):
                try:
                    return (
                        json.dumps(x, ensure_ascii=False)
                        if isinstance(x, (dict, list))
                        else str(x)
                    )
                except Exception:
                    return str(x)

            out_text = _txt(output)

            # LOG tool call to MongoDB
            await save_message(
                uid=uid,
                role="tool",
                text=out_text[:8000],
                conversation_id=conversation_id,
                meta={
                    "tool_name": name,
                    "args": args,
                    "output": output,
                    "latency_ms": elapsed_ms,
                    "error": error_txt,
                    "tool_call_id": tool_call_id,
                    "source": "mcp",
                },
            )

            tool_msgs.append(
                ToolMessage(content=out_text, tool_call_id=tool_call_id, name=name)
            )

        return {"messages": tool_msgs}

    def should_continue(state: AgentState):
        last = state["messages"][-1]
        return (
            "call_tools"
            if isinstance(last, AIMessage) and getattr(last, "tool_calls", None)
            else END
        )

    builder = StateGraph(AgentState)  # ← use our custom state
    builder.add_node("call_model", call_model)
    builder.add_node("call_tools", call_tools)
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges(
        "call_model",
        should_continue,
        {
            "call_tools": "call_tools",
            END: END,
        },
    )
    builder.add_edge("call_tools", "call_model")

    _agent_graph = builder.compile()
    png_data = _agent_graph.get_graph(xray=True).draw_mermaid_png()
    with open("graph_visualization.png", "wb") as f:
        f.write(png_data)

    return _agent_graph
