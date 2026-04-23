from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    # The conversation history
    messages: Annotated[List[BaseMessage], operator.add]
    
    # Intent tracking (greeting, inquiry, lead)
    intent: str 
    
    # Lead details
    name: str
    email: str
    platform: str