from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from state import AgentState
from nodes import router_node, rag_node, lead_node, tools

# 1. Initialize Graph
workflow = StateGraph(AgentState)

# 2. Add the prebuilt ToolNode to your graph
tool_node = ToolNode(tools)

# 3. Add Nodes
workflow.add_node("router", router_node)
workflow.add_node("rag", rag_node)
workflow.add_node("lead", lead_node)
workflow.add_node("tools", tool_node)

# 4. Set Entry Point
workflow.set_entry_point("router")

# 5. Define Conditional Routing from Router
def route_logic(state: AgentState):
    intent = state.get("intent")
    if intent == "inquiry":
        return "rag"
    elif intent == "lead":
        return "lead"
    return END 

workflow.add_conditional_edges("router", route_logic)

# 6. Define Tool Routing from Lead Node
def route_lead(state: AgentState):
    """Checks if the LLM decided to call the tool or just ask a question."""
    last_message = state["messages"][-1]
    
    # If the LLM generated a tool call, route to the execution node
    if getattr(last_message, "tool_calls", None):
        return "tools"
    
    # Otherwise, it's just a conversational response asking for missing data
    return END

workflow.add_conditional_edges("lead", route_lead)

# 7. Add Standard Edges
# After a tool executes, route back to the lead_node so the LLM can see the 
# success message and say a final goodbye to the user.
workflow.add_edge("tools", "lead")
workflow.add_edge("rag", END)

# 8. Compile the Graph
app = workflow.compile()