from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
import operator

class AgentState(TypedDict):
    # The conversation history
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Intent tracking (greeting, inquiry, lead)
    intent: str 
    
    # Lead details
    name: str
    email: str
    platform: str