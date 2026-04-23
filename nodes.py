from state import AgentState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize the LLM (Gemini 2.0 Flash)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)

# Define the expected strict output for the router
class IntentClassification(BaseModel):
    intent: str = Field(
        description="Must be strictly one of: 'greeting', 'inquiry', or 'lead'."
    )

# Define the tool using LangChain's decorator
@tool
def mock_lead_capture(name: str, email: str, platform: str) -> str:
    """
    Call this tool ONLY when you have explicitly collected all three required pieces 
    of information from the user: Name, Email, and Creator Platform.
    """
    print(f"Lead captured successfully: {name}, {email}, {platform}")
    return "Lead successfully captured in the backend database."

# Group tools into a list for binding
tools = [mock_lead_capture]

def router_node(state: AgentState):
    """Analyzes the latest message and categorizes user intent with context."""
    messages = state["messages"]
    last_user_message = messages[-1].content
    
    # Grab the previous AI message to provide context to the router
    context = ""
    if len(messages) >= 2 and messages[-2].type == "ai":
        context = f"Previous AI question: '{messages[-2].content}'"

    prompt = f"""You are an intent routing system for AutoStream, an AI video editing SaaS.
    Analyze the user message and strictly categorize it into one of these intents:
    - 'greeting': Casual hellos, pleasantries.
    - 'inquiry': Questions about pricing, features, plans, or company policies.
    - 'lead': Explicit statements showing readiness to sign up OR the user is providing requested signup details (Name, Email, Platform).

    {context}
    Current User Message: "{last_user_message}"
    
    CRITICAL RULE: If the Previous AI question was asking for signup details (name, email, platform) and the Current User Message is answering it, you MUST classify the intent as 'lead'.
    """
    
    # Force the LLM to return JSON matching the Pydantic model
    structured_llm = llm.with_structured_output(IntentClassification)
    result = structured_llm.invoke(prompt)
    
    return {"intent": result.intent}
def rag_node(state: AgentState):
    """Reads data.md and answers product questions using only that context."""
    # Read the local knowledge base
    with open("data.md", "r") as f:
        kb_content = f.read()
    
    last_user_message = state["messages"][-1].content
    
    system_prompt = f"""You are a customer support agent for AutoStream, an automated video editing SaaS.
    Answer the user's question using strictly the information provided in the Knowledge Base below. 
    Do not hallucinate features or prices. If the answer is not in the data, state that you do not know.
    
    <Knowledge Base>
    {kb_content}
    </Knowledge Base>
    """
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=last_user_message)
    ])
    
    return {"messages": [response]}

def lead_node(state: AgentState):
    """Manages the conversation to extract entities and trigger the tool."""
    # Bind the tool schema to the LLM so it knows it can call it
    llm_with_tools = llm.bind_tools(tools)
    
    system_prompt = """You are an AutoStream onboarding assistant. The user wants to sign up.
    You must collect exactly three pieces of information from the user:
    1. Name
    2. Email
    3. Creator Platform (e.g., YouTube, Instagram, TikTok)
    
    Review the conversation history. If any of these are missing, ask the user for them in a friendly, conversational manner.
    Once you have identified all three pieces of information in the conversation history, you MUST execute the `mock_lead_capture` tool.
    Do not invent or guess any information."""
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}