import os
import requests

def ask_agent(message, user_id, language="en", session_id=None):
    """
    Connects this Streamlit app to the ADK agent running on another laptop/server.

    Configure AGENT_API_URL in .env to point to your teammate's HTTP API.
    Expected request JSON: {message, user_id, language, session_id}
    Expected response JSON: {reply: "..."}
    """
    url = os.getenv("AGENT_API_URL", "").strip()
    if not url:
        return (
            "The Carbon Sync AI agent is not connected yet. "
            "Please start the ADK agent service and set AGENT_API_URL in the .env file. "
            "Your message has been saved in chat history."
        )
    try:
        response = requests.post(
            url,
            json={
                "message": message,
                "user_id": user_id,
                "language": language,
                "session_id": session_id
            },
            timeout=45
        )
        response.raise_for_status()
        data = response.json()
        return data.get("reply") or data.get("response") or "The agent returned an empty response."
    except requests.RequestException as exc:
        return f"Could not reach the AI agent. Check the agent URL and connection. ({exc})"
    except ValueError:
        return "The AI agent response was not valid JSON. Please check the agent API format."
