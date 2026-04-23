# state.py
from langgraph.graph import MessagesState

class AgentState(MessagesState):
    intent: str 
    active_flow: str # The lock variable
    
    name: str
    email: str
    platform: str