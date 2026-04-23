# AutoStream: Social-to-Lead Agentic Workflow

**Author:** Kamran Riyaz

## 1. How to run the project locally

1. **Clone the repository:**

   ```bash
   git clone git@github.com:KamranRiyaz/autostream-agent.git
   cd autostream-agent

   ```

2. **Install Dependencies:**

   ```bash
    pip install -r requirements.txt

   ```

3. **Set up Environment Variables:**
   Create a .env file in the root directory and add your Google Gemini API Key:

   ```bash
   GOOGLE_API_KEY=your_gemini_api_key_here

   ```

4. **Run the Terminal Test**:
   Execute the chat interface to interact with the agent locally.
   ```bash
   python3 test_chat.py
   ```

## 2. Architecture Explanation

1. **Why LangGraph?**

   LangGraph was chosen over AutoGen and standard LangChain chains because this specific ServiceHive workflow requires strict, multi-turn state transitions rather than autonomous, open-ended multi-agent debates.

   LangGraph's cyclic, graph-based architecture provides deterministic routing that enforces rigid conversational boundaries between distinct intents (greeting, inquiry, high-intent lead).

   By utilizing Pydantic structured outputs at the routing node alongside LangChain's native tool-calling, the graph guarantees reliable traversal of execution edges without LLM hallucination, which is critical for transactional enterprise lead-capture systems.

2. **How State is Managed.**

   State is managed using LangGraph's MessagesState, augmented with the built-in MemorySaver checkpointer.

   The state is maintained persistently across the required 5-6 conversation turns using a unique thread_id.

   The state dictionary tracks the messages array and a custom active_flow lock variable.

   When a user explicitly demonstrates high intent to sign up, this lock engages to bypass the stateless intent router for subsequent messages.

   This architectural pattern prevents "context amnesia" and securely holds the user in the lead qualification entity-extraction loop (Name, Email, Platform) until the mock_lead_capture tool successfully fires, after which the state lock is released.

## 3. WhatsApp Deployment

Integrating this LangGraph agent with WhatsApp via Webhooks requires an intermediary architecture to handle the HTTP handshakes between Meta's platform and our Python runtime.

1. **Method 1: Twilio API + Ngrok.**

   We expose the local FastAPI server to a public HTTPS URL using Ngrok. We configure a Twilio WhatsApp Sandbox, pointing its webhook to the Ngrok endpoint. When a user sends a WhatsApp message, Twilio intercepts it and dispatches an application/x-www-form-urlencoded POST request to our FastAPI endpoint. The system extracts the text, invokes the LangGraph agent to generate the response, and returns a structured TwiML XML payload back to Twilio to dispatch to the user.

2. **Method 2: Meta Cloud API.**

    For a production environment, we register a Meta Developer App and host our FastAPI application on a cloud provider. We configure the Meta App with our production webhook URL. Meta sends incoming messages directly as JSON POST payloads to the endpoint. The agent processes the intent, and the backend replies by triggering an asynchronous POST request containing a structured JSON payload directly to Meta's WhatsApp Graph API.
